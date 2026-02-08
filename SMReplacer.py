# meta developer: @sotka_modules
# meta name: SMReplacer

from .. import loader, utils
from telethon import events
import re
import aiohttp

__version__ = (3, 3, 0, 0)

ENG = "qwertyuiop[]asdfghjkl;'zxcvbnm,./"
RUS = "йцукенгшщзхъфывапролджэячсмитьбю."

EN2RU = str.maketrans(ENG + ENG.upper(), RUS + RUS.upper())
RU2EN = str.maketrans(RUS + RUS.upper(), ENG + ENG.upper())

DICT_URL = "https://github.com/danakt/russian-words/raw/refs/heads/master/russian.txt"
WORD_RE = re.compile(r"[а-яА-ЯёЁ]+")


@loader.tds
class SMReplacer(loader.Module):
    """
    Автозамена раскладки EN ↔ RU
    и коррекция текста по словарю
    """

    strings = {
        "name": "SMReplacer",
        "smenru_on": "⌨️ Автозамена раскладки включена",
        "smenru_off": "⌨️ Автозамена раскладки выключена",
        "smcorrect_on": "🧠 Коррекция по словарю включена",
        "smcorrect_off": "🧠 Коррекция по словарю выключена",
        "usage": "Используй: on / off",
    }

    def __init__(self):
        self.smenru = True
        self.smcorrect = True
        self.words = set()
        self.loading = False

    async def client_ready(self, client, db):
        self._client = client
        await self._load_dict()
        client.add_event_handler(
            self.watcher,
            events.NewMessage(outgoing=True)
        )

    async def _load_dict(self):
        if self.words or self.loading:
            return

        self.loading = True
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(DICT_URL) as response:
                    raw = await response.read()

            text = raw.decode("cp1251", errors="ignore")
            self.words = {
                line.strip().lower()
                for line in text.splitlines()
                if line.strip()
            }
        finally:
            self.loading = False

    def _dict_match(self, text):
        return any(
            word in self.words
            for word in WORD_RE.findall(text.lower())
        )

    async def smenrucmd(self, message):
        """
        on / off
        """
        arg = utils.get_args_raw(message).lower()
        if arg == "on":
            self.smenru = True
            await utils.answer(message, self.strings("smenru_on"))
        elif arg == "off":
            self.smenru = False
            await utils.answer(message, self.strings("smenru_off"))
        else:
            await utils.answer(message, self.strings("usage"))

    async def smcorrectcmd(self, message):
        """
        on / off
        """
        arg = utils.get_args_raw(message).lower()
        if arg == "on":
            self.smcorrect = True
            await utils.answer(message, self.strings("smcorrect_on"))
        elif arg == "off":
            self.smcorrect = False
            await utils.answer(message, self.strings("smcorrect_off"))
        else:
            await utils.answer(message, self.strings("usage"))

    async def watcher(self, event):
        if not event.out:
            return

        text = event.raw_text
        if not text or text[0] in ".!/?" :
            return

        if not self.words:
            return

        if self.smenru:
            ru = text.translate(EN2RU)
            if ru != text and (not self.smcorrect or self._dict_match(ru)):
                await event.edit(ru)
                return

            en = text.translate(RU2EN)
            if en != text and not self._dict_match(text):
                await event.edit(en)
