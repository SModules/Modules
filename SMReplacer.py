# meta developer: @sotka_modules
# meta name: SMReplacer

from .. import loader, utils
from telethon import events
import re
import aiohttp

__version__ = (3, 5, 2, 0)

ENG = "qwertyuiop[]asdfghjkl;'zxcvbnm,./"
RUS = "йцукенгшщзхъфывапролджэячсмитьбю."

EN2RU = str.maketrans(ENG + ENG.upper(), RUS + RUS.upper())
RU2EN = str.maketrans(RUS + RUS.upper(), ENG + ENG.upper())

DICT_URL = "https://github.com/danakt/russian-words/raw/refs/heads/master/russian.txt"

WORD_RE = re.compile(r"[а-яА-ЯёЁ]+")
RUS_LETTERS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"


@loader.tds
class SMReplacer(loader.Module):
    """
    SMReplacer

    Умная автозамена раскладки EN ↔ RU
    и автокоррекция опечаток в русских словах.

    Возможности:
    • Исправление ошибок раскладки
    • Автокоррекция слов с одной ошибкой
    • Работа только с твоими сообщениями
    • Правка сообщения через edit, без удаления
    """

    strings = {
        "name": "SMReplacer",
        "smenru_on": "⌨️ Автозамена раскладки включена",
        "smenru_off": "⌨️ Автозамена раскладки выключена",
        "smcorrect_on": "🧠 Автокоррекция включена",
        "smcorrect_off": "🧠 Автокоррекция выключена",
        "usage": "Используй: on / off",
    }

    def __init__(self):
        """
        Изначально все режимы выключены
        """
        self.smenru = False
        self.smcorrect = False
        self.words = set()
        self.loading = False

    async def client_ready(self, client, db):
        """
        Инициализация модуля и загрузка словаря
        """
        self._client = client
        await self._load_dict()
        client.add_event_handler(
            self.watcher,
            events.NewMessage(outgoing=True)
        )

    async def _load_dict(self):
        """
        Загрузка словаря напрямую из публичного репозитория
        Без сохранения на диск
        """
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
        """
        Проверка: есть ли в тексте слова из словаря
        """
        return any(
            w in self.words
            for w in WORD_RE.findall(text.lower())
        )

    def _fix_word(self, word):
        """
        Автокоррекция одного слова
        Допускается одна ошибка
        """
        if word in self.words or len(word) < 3 or len(word) > 20:
            return word

        w = word.lower()

        for i in range(len(w)):
            candidate = w[:i] + w[i+1:]
            if candidate in self.words:
                return candidate

        for i in range(len(w) + 1):
            for c in RUS_LETTERS:
                candidate = w[:i] + c + w[i:]
                if candidate in self.words:
                    return candidate

        for i in range(len(w)):
            for c in RUS_LETTERS:
                if c != w[i]:
                    candidate = w[:i] + c + w[i+1:]
                    if candidate in self.words:
                        return candidate

        for i in range(len(w) - 1):
            candidate = w[:i] + w[i+1] + w[i] + w[i+2:]
            if candidate in self.words:
                return candidate

        return word

    def _autocorrect(self, text):
        """
        Автокоррекция всех слов в тексте
        """
        def repl(match):
            word = match.group(0)
            fixed = self._fix_word(word)
            return fixed if word.islower() else fixed.capitalize()

        return WORD_RE.sub(repl, text)

    async def smenrucmd(self, message):
        """
        Включить или выключить автозамену раскладки
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
        Включить или выключить автокоррекцию
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
        """
        Основная логика обработки сообщений
        """
        if not event.out:
            return

        text = event.raw_text
        if not text or text[0] in ".!/?" :
            return

        if not self.words:
            return

        new = text

        if self.smenru:
            ru = new.translate(EN2RU)
            if ru != new and (not self.smcorrect or self._dict_match(ru)):
                new = ru

            en = new.translate(RU2EN)
            if en != new and not self._dict_match(new):
                new = en

        if self.smcorrect:
            new = self._autocorrect(new)

        if new != text:
            await event.edit(new)
