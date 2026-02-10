# meta developer: @sotka_modules
# meta name: SMGlRestrict

from .. import loader, utils
from telethon.tl.types import Chat, Channel, Message
import time
import re

__version__ = (1, 4, 2, 5)


@loader.tds
class SMGlRestrict(loader.Module):
    """
    SMGlRestrict

    Global ban / mute user
    in all chats where you are an admin.
    Supports time and reason.
    """

    strings = {
        "name": "SMGlRestrict",
        "no_args": "❌ <b>Specify a user or reply to a message.</b>",
        "ban_start": "🚫 <b>Global ban</b>: <code>{}</code>",
        "ban_done": "🚫 <b>Banned in {} chats.</b>",
        "unban_done": "✅ <b>Unbanned in {} chats.</b>",
        "mute_start": "🔇 <b>Global mute</b>: <code>{}</code>",
        "mute_done": "🔇 <b>Muted in {} chats.</b>",
        "unmute_done": "🔊 <b>Unmuted in {} chats.</b>",
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

    async def _get_target(self, message: Message):
        args = utils.get_args(message)
        if args:
            try:
                return await self._client.get_entity(args[0])
            except Exception:
                return None

        reply = await message.get_reply_message()
        if reply:
            return await self._client.get_entity(reply.sender_id)

        return None

    async def _iter_admin_chats(self):
        async for dialog in self._client.iter_dialogs():
            chat = dialog.entity

            if not isinstance(chat, (Chat, Channel)):
                continue

            if isinstance(chat, Channel) and not chat.megagroup:
                continue

            rights = getattr(chat, "admin_rights", None)
            if not rights or not rights.ban_users:
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
        args = utils.get_args(message)
        duration = 0
        reason = "Not specified"

        if len(args) >= 2:
            duration = self._parse_time(args[1])
            if len(args) > 2:
                reason = " ".join(args[2:])
        elif len(args) == 1:
            duration = self._parse_time(args[0])

        return duration, reason

    # ---------- commands ----------

    @loader.command(
        ru_doc="<reply | user> [time] [reason] — globally ban user",
        en_doc="<reply | user> [time] [reason] — globally ban user",
    )
    async def glbancmd(self, message: Message):
        user = await self._get_target(message)
        if not user:
            await utils.answer(message, self.strings("no_args"))
            return

        duration, reason = self._parse_args(message)
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
        ru_doc="<reply | user> — globally unban user",
        en_doc="<reply | user> — globally unban user",
    )
    async def glunbancmd(self, message: Message):
        user = await self._get_target(message)
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
        ru_doc="<reply | user> [time] [reason] — globally mute user",
        en_doc="<reply | user> [time] [reason] — globally mute user",
    )
    async def glmutecmd(self, message: Message):
        user = await self._get_target(message)
        if not user:
            await utils.answer(message, self.strings("no_args"))
            return

        duration, reason = self._parse_args(message)
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
        ru_doc="<reply | user> — globally unmute user",
        en_doc="<reply | user> — globally unmute user",
    )
    async def glunmutecmd(self, message: Message):
        user = await self._get_target(message)
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
