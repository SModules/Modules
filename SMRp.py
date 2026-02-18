# meta developer: @sotka_modules
# meta name: RPExtended

from .. import loader, utils

__version__ = (1, 5, 0, 0)


@loader.tds
class RPAdvanced(loader.Module):
    """
    RPAdvanced Correct Order
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

        action_text = f"{base_action} {target}"
        if extra_action:
            action_text += f" {extra_action}"

        text = f"👤 <b>{action_text}</b>"

        if replica:
            text += f'\n💬 <i>"{replica}"</i>'

        await message.edit(text, parse_mode="html")

    # =========================
    # 💞 Обычные RP
    # =========================

    async def rhugcmd(self, message):
        """Обнять пользователя"""
        await self._send(message, "обнял")

    async def rkisscmd(self, message):
        """Поцеловать пользователя"""
        await self._send(message, "поцеловал")

    async def rslapcmd(self, message):
        """Дать пощёчину"""
        await self._send(message, "дал пощёчину")

    async def rpunchcmd(self, message):
        """Ударить"""
        await self._send(message, "ударил")

    async def rbitecmd(self, message):
        """Укусить"""
        await self._send(message, "укусил")

    async def rpatcmd(self, message):
        """Погладить"""
        await self._send(message, "погладил")

    async def rcuddlecmd(self, message):
        """Прижать к себе"""
        await self._send(message, "прижал к себе")

    async def rlickcmd(self, message):
        """Лизнуть"""
        await self._send(message, "лизнул")

    async def rspankcmd(self, message):
        """Шлёпнуть"""
        await self._send(message, "шлёпнул")

    async def rlovecmd(self, message):
        """Страстно поцеловать"""
        await self._send(message, "страстно поцеловал")

    # =========================
    # 🔥 18+ RP
    # =========================

    async def rmoancmd(self, message):
        """Простонать"""
        await self._send(message, "возбуждённо простонал возле")

    async def rteasecmd(self, message):
        """Подразнить"""
        await self._send(message, "дразняще провёл рукой по")

    async def rgripcmd(self, message):
        """Грубо притянуть"""
        await self._send(message, "грубо притянул к себе")

    async def rwhispercmd(self, message):
        """Шепнуть на ухо"""
        await self._send(message, "шепнул на ухо")

    async def rpinchcmd(self, message):
        """Игриво прикусить"""
        await self._send(message, "игриво прикусил")

    async def rdomcmd(self, message):
        """Прижать к стене"""
        await self._send(message, "прижал к стене")

    async def rstripcmd(self, message):
        """Провести взглядом"""
        await self._send(message, "медленно провёл взглядом по")

    async def rheatcmd(self, message):
        """Жарко прижать"""
        await self._send(message, "жарко прижал к себе")

    async def rclaimcmd(self, message):
        """Собственнически обнять"""
        await self._send(message, "собственнически обнял")

    async def rdesirecmd(self, message):
        """Прошептать с желанием"""
        await self._send(message, "прошептал с желанием")
