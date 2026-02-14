# meta developer: @sotka_modules
# meta name: RPExtended

from .. import loader, utils

__version__ = (1, 1, 4, 3)


@loader.tds
class RPAdvanced(loader.Module):
    """
    RPAdvanced
    """

    strings = {
        "name": "RPAdvanced"
    }

    async def _target(self, message):
        reply = await message.get_reply_message()
        if not reply:
            return None, None

        user = await reply.get_sender()
        link = f'<a href="tg://user?id={user.id}">{user.first_name}</a>'
        return reply, link

    async def _send(self, message, base_action):
        reply, target = await self._target(message)
        if not reply:
            return await utils.answer(message, "Reply to someone")

        extra = utils.get_args_raw(message)
        action = f"{base_action} {extra}".strip()

        text = f"👤 <b>{action}</b> {target}"
        await message.edit(text, parse_mode="html")

    async def rhugcmd(self, message):
        """reply"""
        await self._send(message, "обнял")

    async def rkisscmd(self, message):
        """reply"""
        await self._send(message, "поцеловал")

    async def rslapcmd(self, message):
        """reply"""
        await self._send(message, "дал пощёчину")

    async def rpunchcmd(self, message):
        """reply"""
        await self._send(message, "ударил")

    async def rbitecmd(self, message):
        """reply"""
        await self._send(message, "укусил")

    async def rpatcmd(self, message):
        """reply"""
        await self._send(message, "погладил")

    async def rcuddlecmd(self, message):
        """reply"""
        await self._send(message, "прижал к себе")

    async def rlickcmd(self, message):
        """reply"""
        await self._send(message, "лизнул")

    async def rspankcmd(self, message):
        """reply"""
        await self._send(message, "шлёпнул")

    async def rlovecmd(self, message):
        """reply"""
        await self._send(message, "страстно поцеловал")
