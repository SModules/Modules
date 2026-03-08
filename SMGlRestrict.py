# meta developer: @sotka_modules
# meta name: SMGlRestrict

from .. import loader, utils
from telethon.tl.types import Chat, Channel, Message
import time
import re

__version__ = (1, 4, 3, 1)


@loader.tds
class SMGlRestrict(loader.Module):
    """
    SMGlRestrict

    Global ban / mute user
    in all chats and channels where you are an admin.
    Supports -u user, -t time, -r reason
    """

    strings = {
        "name": "SMGlRestrict",
        "no_args": "❌ <b>Specify a user (with -u) or reply to a message.</b>",
        "ban_start": "🚫 <b>Global ban</b>: <code>{}</code>",
        "ban_done": "🚫 <b>Banned in {} chats/channels.</b>",
        "unban_done": "✅ <b>Unbanned in {} chats/channels.</b>",
        "mute_start": "🔇 <b>Global mute</b>: <code>{}</code>",
        "mute_done": "🔇 <b>Muted in {} chats/channels.</b>",
        "unmute_done": "🔊 <b>Unmuted in {} chats/channels.</b>",
    }

    # ---------- helpers ----------

    def _get_name(self, user):
        if hasattr(user, "title"):
            return utils.escape_html(user.title)

        first = getattr(user, "first_name", "") or ""
        last = getattr(user, "last_name", "") or ""
        return utils.escape_html(f"{first} {last}".strip() or "user")

    def _parse_time(self, text: str) -> int:
        """
        Parse time like: 10m / 2h / 3d / 30s
        """
        if not text:
            return 0

        m = re.match(r"^(\d+)([smhd])$", text.lower())
        if not m:
            return 0

        value, unit = m.groups()
        value = int(value)

        return {
            "s": value,
            "m": value * 60,
            "h": value * 3600,
            "d": value * 86400,
        }[unit]

    async def _get_target(self, message: Message, user_arg: str = None):
        """
        Получает пользователя по:
        - username, id или tg://user?id=123
        - reply, если нет аргумента
        """
        if user_arg:
            user_arg = user_arg.strip()
            # tg://user?id=123
            tg_match = re.match(r"tg://user\?id=(\d+)", user_arg)
            if tg_match:
                return await self._client.get_entity(int(tg_match.group(1)))
            try:
                return await self._client.get_entity(user_arg)
            except Exception:
                return None

        # reply fallback
        reply = await message.get_reply_message()
        if reply:
            return await self._client.get_entity(reply.sender_id)

        return None

    async def _iter_admin_chats(self):
        async for dialog in self._client.iter_dialogs():
            chat = dialog.entity
            if not isinstance(chat, (Chat, Channel)):
                continue

            rights = getattr(chat, "admin_rights", None)
            if isinstance(chat, Channel) and not rights:
                try:
                    full = await self._client.get_permissions(chat, "me")
                    if full.is_admin or full.is_owner:
                        rights = full
                except Exception:
                    continue

            if not rights or not getattr(rights, "ban_users", True):
                continue

            yield chat

    async def _restrict(self, user, rights, until_date=0):
        count = 0
        async for chat in self._iter_admin_chats():
            try:
                await self._client.edit_permissions(
                    chat,
                    user,
                    until_date=until_date,
                    **rights,
                )
                count += 1
            except Exception:
                pass
        return count

    def _parse_args(self, message: Message):
        """
        Парсим аргументы:
        -u <user>
        -t <time>
        -r <reason>
        """
        args = utils.get_args_raw(message)
        user = None
        duration = 0
        reason = "Not specified"

        if not args:
            return user, duration, reason

        # простой парсер
        u_match = re.search(r"-u\s+(\S+)", args)
        t_match = re.search(r"-t\s+(\S+)", args)
        r_match = re.search(r"-r\s+(.+)", args)

        if u_match:
            user = u_match.group(1)
        if t_match:
            duration = self._parse_time(t_match.group(1))
        if r_match:
            reason = r_match.group(1).strip()

        return user, duration, reason

    # ---------- commands ----------

    @loader.command(
        ru_doc="-u <user> -t <time> -r <reason> — глобальный бан",
        en_doc="-u <user> -t <time> -r <reason> — globally ban user",
    )
    async def glbancmd(self, message: Message):
        user_arg, duration, reason = self._parse_args(message)
        user = await self._get_target(message, user_arg)
        if not user:
            await utils.answer(message, self.strings("no_args"))
            return

        until = int(time.time() + duration) if duration else 0
        name = self._get_name(user)
        await utils.answer(message, self.strings("ban_start").format(name))

        count = await self._restrict(
            user,
            dict.fromkeys(
                [
                    "view_messages",
                    "send_messages",
                    "send_media",
                    "send_stickers",
                    "send_gifs",
                    "send_games",
                    "send_inline",
                    "send_polls",
                    "change_info",
                    "invite_users",
                ],
                False,
            ),
            until,
        )

        await utils.answer(
            message,
            f"{self.strings('ban_done').format(count)}\n"
            f"<b>Reason:</b> <i>{utils.escape_html(reason)}</i>",
        )

    @loader.command(
        ru_doc="-u <user> — глобальный разбан",
        en_doc="-u <user> — globally unban user",
    )
    async def glunbancmd(self, message: Message):
        user_arg, _, _ = self._parse_args(message)
        user = await self._get_target(message, user_arg)
        if not user:
            await utils.answer(message, self.strings("no_args"))
            return

        count = await self._restrict(
            user,
            dict.fromkeys(
                [
                    "view_messages",
                    "send_messages",
                    "send_media",
                    "send_stickers",
                    "send_gifs",
                    "send_games",
                    "send_inline",
                    "send_polls",
                    "change_info",
                    "invite_users",
                ],
                True,
            ),
            0,
        )

        await utils.answer(message, self.strings("unban_done").format(count))

    @loader.command(
        ru_doc="-u <user> -t <time> -r <reason> — глобальный мут",
        en_doc="-u <user> -t <time> -r <reason> — globally mute user",
    )
    async def glmutecmd(self, message: Message):
        user_arg, duration, reason = self._parse_args(message)
        user = await self._get_target(message, user_arg)
        if not user:
            await utils.answer(message, self.strings("no_args"))
            return

        until = int(time.time() + duration) if duration else 0
        name = self._get_name(user)
        await utils.answer(message, self.strings("mute_start").format(name))

        count = await self._restrict(
            user,
            {
                "view_messages": True,
                "send_messages": False,
                "send_media": False,
                "send_stickers": False,
                "send_gifs": False,
                "send_games": False,
                "send_inline": False,
                "send_polls": False,
                "change_info": False,
                "invite_users": False,
            },
            until,
        )

        await utils.answer(
            message,
            f"{self.strings('mute_done').format(count)}\n"
            f"<b>Reason:</b> <i>{utils.escape_html(reason)}</i>",
        )

    @loader.command(
        ru_doc="-u <user> — глобальный разму́т",
        en_doc="-u <user> — globally unmute user",
    )
    async def glunmutecmd(self, message: Message):
        user_arg, _, _ = self._parse_args(message)
        user = await self._get_target(message, user_arg)
        if not user:
            await utils.answer(message, self.strings("no_args"))
            return

        count = await self._restrict(
            user,
            {
                "view_messages": True,
                "send_messages": True,
                "send_media": True,
                "send_stickers": True,
                "send_gifs": True,
                "send_games": True,
                "send_inline": True,
                "send_polls": True,
                "change_info": True,
                "invite_users": True,
            },
            0,
        )

        await utils.answer(message, self.strings("unmute_done").format(count))
