# meta developer: @sotka_modules
# meta name: RPExtended

from .. import loader, utils

__version__ = (1, 5, 2, 0)


@loader.tds
class RPExtended(loader.Module):
    """
    RPExtended
    """

    strings = {
        "name": "RPExtended"
    }

    async def _do(self, message, action):
        reply = await message.get_reply_message()
        if not reply:
            return await utils.answer(message, "Reply to someone")

        user = await reply.get_sender()
        target = f"@{user.username}" if user.username else user.first_name

        await message.edit(f"* {action} {target} *")

    async def rhugcmd(self, message):
        """reply"""
        await self._do(message, "обнял")

    async def rkisscmd(self, message):
        """reply"""
        await self._do(message, "поцеловал")

    async def rslapcmd(self, message):
        """reply"""
        await self._do(message, "дал пощёчину")

    async def rpunchcmd(self, message):
        """reply"""
        await self._do(message, "ударил")

    async def rbitecmd(self, message):
        """reply"""
        await self._do(message, "укусил")

    async def rpatcmd(self, message):
        """reply"""
        await self._do(message, "погладил")

    async def rcuddlecmd(self, message):
        """reply"""
        await self._do(message, "прижал к себе")

    async def rlickcmd(self, message):
        """reply"""
        await self._do(message, "лизнул")

    async def rspankcmd(self, message):
        """reply"""
        await self._do(message, "шлёпнул")

    async def rfuckcmd(self, message):
        """reply"""
        await self._do(message, "жёстко занялся с")
