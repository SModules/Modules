# meta developer: @sotka_modules
# meta name: SMGlRestrict

from .. import loader, utils
from telethon.tl.types import Chat, Channel, Message

__version__ = (1, 4, 2, 5)


@loader.tds
class SMGlRestrict(loader.Module):
    """
    SMGlRestrict

    Глобальный бан / мут во всех чатах,
    где ты администратор с ban_users.
    """

    strings = {
        "name": "SMGlRestrict",
        "no_args": "❌ <b>Укажи пользователя или ответь на сообщение.</b>",
        "ban_start": "🚫 <b>Глобальный бан</b>: <code>{}</code>",
        "ban_done": "🚫 <b>Забанен в {} чатах.</b>",
        "unban_start": "✅ <b>Глобальный разбан</b>: <code>{}</code>",
        "unban_done": "✅ <b>Разбанен в {} чатах.</b>",
        "mute_start": "🔇 <b>Глобальный мут</b>: <code>{}</code>",
        "mute_done": "🔇 <b>Замучен в {} чатах.</b>",
        "unmute_start": "🔊 <b>Глобальный размут</b>: <code>{}</code>",
        "unmute_done": "🔊 <b>Размучен в {} чатах.</b>",
    }

    def _get_name(self, user):
        if hasattr(user, "title"):
            return utils.escape_html(user.title)

        first = getattr(user, "first_name", "") or ""
        last = getattr(user, "last_name", "") or ""
        return utils.escape_html(f"{first} {last}".strip() or "user")

    async def _get_target(self, message: Message):
        args = utils.get_args(message)
        if args:
            try:
                return await self._client.get_entity(args[0])
            except Exception:
                return None

        reply = await message.get_reply_message()
        if reply:
            try:
                return await self._client.get_entity(reply.sender_id)
            except Exception:
                return None

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

    async def _restrict(self, user, rights):
        count = 0

        async for chat in self._iter_admin_chats():
            try:
                await self._client.edit_permissions(chat, user, **rights)
                count += 1
            except Exception:
                pass

        return count

    @loader.command()
    async def glbancmd(self, message: Message):
        user = await self._get_target(message)
        if not user:
            await utils.answer(message, self.strings("no_args"))
            return

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
        )

        await utils.answer(message, self.strings("ban_done").format(count))
