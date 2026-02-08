# meta developer: @sotka_modules
# meta name: SMReplacer

from .. import loader, utils
from telethon import events
from pathlib import Path
import re
import aiohttp

__version__ = (3, 1, 0, 0)

ENG = "qwertyuiop[]asdfghjkl;'zxcvbnm,./"
RUS = "йцукенгшщзхъфывапролджэячсмитьбю."

EN2RU = str.maketrans(ENG + ENG.upper(), RUS + RUS.upper())
RU2EN = str.maketrans(RUS + RUS.upper(), ENG + ENG.upper())

DICT_URL = "https://github.com/danakt/russian-words/raw/refs/heads/master/russian.txt"
WORD_RE = re.compile(r"[а-яА-ЯёЁ]+")


@loader.tds
class SMReplacer(loader.Module):
    """
    Умная автозамена раскладки EN ↔ RU
    и корректирование слов по словарю русского языка
    """

    strings = {
        "name": "SMReplacer",
        "smenru_on": "⌨️ Автозамена раскладки включена",
        "smenru_off": "⌨️ Автозамена раскладки выключена",
        "smcorrect_on": "🧠 Коррекция слов включена",
        "smcorrect_off": "🧠 Коррекция слов выключена",
        "dict_loading": "📥 Загружаю словарь русского языка…",
        "dict_loaded": "📚 Словарь загружен: {} слов",
        "dict_error": "⚠️ Не удалось загрузить словарь",
        "usage": "Используй: on / off"
    }

    def __init__(self):
        self.smenru = True
        self.smcorrect = True
        self.words = set()
        self.dict_path = Path(__file__).with_name("russian_words.txt")

    async def client_ready(self, client, db):
        self._client = client
        await self._load_dict()
        client.add_event_handler(
            self.watcher,
            events.NewMessage(outgoing=True)
        )

    async def _load_dict(self):
        if self.dict_path.exists():
            self._read_dict()
            return

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(DICT_URL) as response:
                    raw = await response.read()

            text = raw.decode("cp1251", errors="ignore")
            self.dict_path.write_text(text, encoding="utf-8")
            self._read_dict()
        except Exception:
            pass

    def _read_dict(self):
        with self.dict_path.open(encoding="utf-8") as file:
            self.words = {
                line.strip().lower()
                for line in file
                if line.strip()
            }

    def _dict_match(self, text):
        return any(
            word in self.words
            for word in WORD_RE.findall(text.lower())
        )

    @loader.command()
    async def smenru(self, message):
        """
        Автозамена раскладки EN ↔ RU
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

    @loader.command()
    async def smcorrect(self, message):
        """
        Коррекция слов по словарю
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
        text = event.raw_text
        if not text or text[0] in ".!/?" :
            return

        if self.smenru:
            ru = text.translate(EN2RU)
            if ru != text and (not self.smcorrect or self._dict_match(ru)):
                await event.delete()
                await self._client.send_message(
                    event.chat_id,
                    ru,
                    reply_to=event.reply_to_msg_id
                )
                return

            en = text.translate(RU2EN)
            if en != text and not self._dict_match(text):
                await event.delete()
                await self._client.send_message(
                    event.chat_id,
                    en,
                    reply_to=event.reply_to_msg_id
                )
