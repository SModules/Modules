# meta developer: @sotka_modules
# meta name: RPExtended

from .. import loader, utils

__version__ = (1, 2, 0, 0)


@loader.tds
class RPAdvanced(loader.Module):
    """
    RPAdvanced with 18+ commands
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

        args = utils.get_args_raw(message)

        parts = args.split("\n", 1) if args else []
        extra_action = parts[0].strip() if parts else ""
        replica = parts[1].strip() if len(parts) > 1 else ""

        action = f"{base_action} {extra_action}".strip()

        text = f"👤 действие {target} <b>{action}</b>"

        if replica:
            text += f'\n💬 <i>"{replica}"</i>'

        await message.edit(text, parse_mode="html")

    # ===================
    # 💞 Обычные RP
    # ===================

    async def rhugcmd(self, message):
        await self._send(message, "обнял")

    async def rkisscmd(self, message):
        await self._send(message, "поцеловал")

    async def rslapcmd(self, message):
        await self._send(message, "дал пощёчину")

    async def rpunchcmd(self, message):
        await self._send(message, "ударил")

    async def rbitecmd(self, message):
        await self._send(message, "укусил")

    async def rpatcmd(self, message):
        await self._send(message, "погладил")

    async def rcuddlecmd(self, message):
        await self._send(message, "прижал к себе")

    async def rlickcmd(self, message):
        await self._send(message, "лизнул")

    async def rspankcmd(self, message):
        await self._send(message, "шлёпнул")

    async def rlovecmd(self, message):
        await self._send(message, "страстно поцеловал")

    # ===================
    # 🔥 18+ RP
    # ===================

    async def rmoancmd(self, message):
        await self._send(message, "возбуждённо простонал возле")

    async def rteasecmd(self, message):
        await self._send(message, "дразняще провёл рукой по")

    async def rgripcmd(self, message):
        await self._send(message, "грубо притянул к себе")

    async def rwhispercmd(self, message):
        await self._send(message, "шепнул на ухо")

    async def rpinchcmd(self, message):
        await self._send(message, "игриво прикусил")

    async def rdomcmd(self, message):
        await self._send(message, "прижал к стене")

    async def rstripcmd(self, message):
        await self._send(message, "медленно провёл взглядом по")

    async def rheatcmd(self, message):
        await self._send(message, "жарко прижал к себе")

    async def rclaimcmd(self, message):
        await self._send(message, "собственнически обнял")

    async def rdesirecmd(self, message):
        await self._send(message, "прошептал с желанием")
