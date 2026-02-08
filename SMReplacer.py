# meta developer: @sotka_modules
# meta name: SMReplacer

__version__ = (1, 4, 8, 8)

from .. import loader, utils
from telethon import events

ENG = "qwertyuiop[]asdfghjkl;'zxcvbnm,./"
RUS = "йцукенгшщзхъфывапролджэячсмитьбю."

TRANS = str.maketrans(
    ENG + ENG.upper(),
    RUS + RUS.upper()
)


@loader.tds
class SMReplacer(loader.Module):
    """Автозамена EN → RU раскладки"""

    strings = {
        "name": "SMReplacer",
        "on": "✅ SMReplacer включён",
        "off": "❌ SMReplacer выключен",
        "usage": "Используй: .smr on / .smr off",
    }

    def __init__(self):
        self.enabled = True

    @loader.command()
    async def smr(self, message):
        args = utils.get_args_raw(message).lower()

        if args == "on":
            self.enabled = True
            await utils.answer(message, self.strings("on"))
        elif args == "off":
            self.enabled = False
            await utils.answer(message, self.strings("off"))
        else:
            await utils.answer(message, self.strings("usage"))

    async def client_ready(self, client, db):
        self._client = client
        client.add_event_handler(
            self.watcher,
            events.NewMessage(outgoing=True)
        )

    async def watcher(self, event):
        if not self.enabled:
            return

        text = event.raw_text
        if not text:
            return

        # не трогаем команды
        if text.startswith((".", "/", "!", "?")):
            return

        fixed = text.translate(TRANS)
        if fixed != text:
            await event.delete()
            await self._client.send_message(
                event.chat_id,
                fixed,
                reply_to=event.reply_to_msg_id
            )
