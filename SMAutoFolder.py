# meta developer: @sotka_modules
# meta name: SMAutoFolder

from .. import loader, utils
from telethon import events
from datetime import datetime, timedelta

__version__ = (1, 1, 0, 0)


@loader.tds
class AutoFolder(loader.Module):
    """
    SMAutoFolder
    """

    strings = {
        "name": "AutoFolder",
        "on": "📁 AutoFolder включён",
        "off": "📁 AutoFolder выключен",
        "status": (
            "📂 AutoFolder: {state}\n"
            "Режим: {mode}\n"
            "Таймер: {hours}ч\n"
            "Игнор: {ignore}"
        ),
        "mode_archive": "архив",
        "mode_unarchive": "разархив",
        "mode_both": "оба",
    }

    def __init__(self):
        self.enabled = False
        self.mode = "both"
        self.timeout = timedelta(hours=48)
        self.ignore = set()
        self.last_out = {}

    async def client_ready(self, client, db):
        self._client = client
        client.add_event_handler(
            self.watcher,
            events.NewMessage()
        )

    async def autofoldercmd(self, message):
        """
        on/off/status/archive/unarchive/both/time/ignore
        """
        args = utils.get_args_raw(message).split()

        if not args:
            return

        cmd = args[0]

        if cmd == "on":
            self.enabled = True
            await utils.answer(message, self.strings("on"))

        elif cmd == "off":
            self.enabled = False
            await utils.answer(message, self.strings("off"))

        elif cmd == "archive":
            self.mode = "archive"
            await utils.answer(message, "📥 Режим: архив")

        elif cmd == "unarchive":
            self.mode = "unarchive"
            await utils.answer(message, "📤 Режим: разархив")

        elif cmd == "both":
            self.mode = "both"
            await utils.answer(message, "🔁 Режим: архив + разархив")

        elif cmd == "time" and len(args) > 1:
            try:
                hours = int(args[1])
                self.timeout = timedelta(hours=hours)
                await utils.answer(message, f"⏱ Таймер: {hours}ч")
            except Exception:
                pass

        elif cmd == "ignore":
            chat = await message.get_chat()
            self.ignore.add(chat.id)
            await utils.answer(message, "🚫 Чат добавлен в ignore")

        elif cmd == "status":
            await utils.answer(
                message,
                self.strings("status").format(
                    state="on" if self.enabled else "off",
                    mode=self.strings(f"mode_{self.mode}"),
                    hours=int(self.timeout.total_seconds() // 3600),
                    ignore=len(self.ignore),
                ),
            )

    async def watcher(self, event):
        if not self.enabled:
            return

        if not event.is_private:
            return

        chat = await event.get_chat()

        if chat.bot or chat.id in self.ignore:
            return

        now = datetime.utcnow()

        if event.out:
            self.last_out[chat.id] = now
            if self.mode in ("unarchive", "both"):
                try:
                    await self._client.edit_folder(chat.id, 0)
                except Exception:
                    pass
            return

        last = self.last_out.get(chat.id)

        if last and now - last > self.timeout:
            if self.mode in ("archive", "both"):
                try:
                    await self._client.edit_folder(chat.id, 1)
                except Exception:
                    pass
