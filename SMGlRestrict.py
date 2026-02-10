# meta developer: @sotka_modules
# meta name: SMGlRestrict

from .. import loader, utils
from telethon.tl.types import Chat, Channel, Message

__version__ = (1, 4, 2, 5)


@loader.tds
class SMGlRestrict(loader.Module):
    """
    SMGlRestrict

    Глобальный бан / мут пользователя
    во всех чатах, где ты администратор
    с правом ban_users.
    """

    strings = {
        "name": "SMGlRestrict",
        "no_args": "❌ <b>Укажи пользователя или ответь на сообщение.</b>",
        "ban_start": "🚫 <b>Глобальный бан {}</b>",
        "ban_done": "🚫 <b>Забанен в {} чатах.</b>",
        "unban_start": "✅ <b>Глобальный разбан {}</b>",
        "unban_done": "✅ <b>Разбанен в {} чатах.</b>",
        "mute_start": "🔇 <b>Глобальный мут {}</b>",
        "mute_done": "🔇 <b>Замучен в {} чатах.</b>",
        "unmute_start": "🔊 <b>Глобальный размут {}</b>",
        "unmute_done": "🔊 <b>Размучен в {} чатах.</b>",
    }

    # ---------- utils ----------

    def _get_name(self, user):
        if hasattr(user, "title"):
            return utils.escape_html(user.title)

        return utils.escape_html(
            f"{getattr(user, 'first_name', '') or ''} "
            f"{getattr(user, 'last_name', '') or ''}".strip()
        )

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
            entity = dialog.entity

            if not isinstance(entity, (Chat, Channel)):
                continue

            if isinstance(entity, Channel) and not entity.megagroup:
                continue

            rights = getattr(entity, "admin_rights", None)
            if not rights or not rights.ban_users:
                continue

            yield entity

    async def _restrict(self, user, rights: dict):
        count = 0

        async for chat in self._iter_admin_chats():
            try:
                await self._client.edit_permissions(chat, user, **rights)
                count += 1
            except Exception:
                pass

        return count

    # ---------- commands ----------

    @loader.command(
        ru_doc="<реплай | юзер> — глобально забанить",
    )
    async def glbancmd(self, message: Message):
        user = await self._get_target(message)
        if not user:
            await utils.answer(message, self.strings("no_args"))
            return

        name = self._get_name(user)
        await utils.answer(message, self.strings("ban_start").format(name))

        count = await self._restrict(
            user,
            {
                "view_messages": False,
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
        )

        await utils.answer(message, self.strings("ban_done").format(count))

    @loader.command(
        ru_doc="<реплай | юзер> — глобально разбанить",
    )
    async def glunbancmd(self, message: Message):
        user = await self._get_target(message)
        if not user:
            await utils.answer(message, self.strings("no_args"))
            return

        name = self._get_name(user)
        await utils.answer(message, self.strings("unban_start").format(name))

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
        )

        await utils.answer(message, self.strings("unban_done").format(count))

    @loader.command(
        ru_doc="<реплай | юзер> — глобально замутить",
    )
    async def glmutecmd(self, message: Message):
        user = await self._get_target(message)
        if not user:
            await utils.answer(message, self.strings("no_args"))
            return

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
        )

        await utils.answer(message, self.strings("mute_done").format(count))

    @loader.command(
        ru_doc="<реплай | юзер> — глобально размутить",
    )
    async def glunmutecmd(self, message: Message):
        user = await self._get_target(message)
        if not user:
            await utils.answer(message, self.strings("no_args"))
            return

        name = self._get_name(user)
        await utils.answer(message, self.strings("unmute_start").format(name))

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
        )

        await utils.answer(message, self.strings("unmute_done").format(count))
