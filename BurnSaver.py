"""
    🔥 BurnSaver - Сохраняет самоуничтожающиеся фото и видео

    Автоматически перехватывает сгорающие фото/видео
    и сохраняет их в Избранное до того как они исчезнут.
"""

version = (1, 0, 0)

# meta developer: @sotka_modules
# meta banner: https://x0.at/uG9P.jpg
# scope: hikka_only

# ███████╗███╗   ███╗ ██████╗ ██████╗ ██╗   ██╗██╗     ███████╗███████╗
# ██╔════╝████╗ ████║██╔═══██╗██╔══██╗██║   ██║██║     ██╔════╝██╔════╝
# ███████╗██╔████╔██║██║   ██║██║  ██║██║   ██║██║     █████╗  ███████╗
# ╚════██║██║╚██╔╝██║██║   ██║██║  ██║██║   ██║██║     ██╔══╝  ╚════██║
# ███████║██║ ╚═╝ ██║╚██████╔╝██████╔╝╚██████╔╝███████╗███████╗███████║
# ╚══════╝╚═╝     ╚═╝ ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝╚══════╝╚══════╝
# © 2026 @sotka_modules | All rights reserved
# ⛔ Копирование без разрешения запрещено

from .. import loader, utils
from herokutl.types import Message
from herokutl.tl.types import MessageMediaPhoto, MessageMediaDocument
import logging

logger = logging.getLogger(__name__)


@loader.tds
class BurnSaverMod(loader.Module):
    """Сохраняет самоуничтожающиеся фото и видео в Избранное"""

    version = (1, 0, 0)

    strings = {
        "name": "BurnSaver",
        "enabled": "🔥 <b>BurnSaver включён.</b> Сгорающие фото/видео будут сохраняться в Избранное.",
        "disabled": "✅ <b>BurnSaver выключен.</b>",
        "saved": "🔥 Сохранено сгорающее медиа от <code>{}</code>",
        "status_on": "🔥 <b>BurnSaver включён.</b>\nСохранено за сессию: <code>{}</code>",
        "status_off": "❌ <b>BurnSaver выключен.</b>",
    }

    strings_ru = {
        "enabled": "🔥 <b>BurnSaver включён.</b> Сгорающие фото/видео будут сохраняться в Избранное.",
        "disabled": "✅ <b>BurnSaver выключен.</b>",
        "saved": "🔥 Сохранено сгорающее медиа от <code>{}</code>",
        "status_on": "🔥 <b>BurnSaver включён.</b>\nСохранено за сессию: <code>{}</code>",
        "status_off": "❌ <b>BurnSaver выключен.</b>",
    }

    def __init__(self):
        self._saved = 0

    async def client_ready(self, client, db):
        self._client = client
        self._db = db

    def _is_burn(self, message) -> bool:
        media = message.media
        if isinstance(media, MessageMediaPhoto):
            photo = media.photo
            if getattr(media, "ttl_seconds", None):
                return True
        if isinstance(media, MessageMediaDocument):
            if getattr(media, "ttl_seconds", None):
                return True
        return False

    def _get_sender_name(self, message) -> str:
        sender = getattr(message, "sender", None)
        if not sender:
            return "unknown"
        name = getattr(sender, "first_name", "") or ""
        username = getattr(sender, "username", None)
        if username:
            return f"@{username}"
        return name or str(sender.id)

    @loader.watcher(only_messages=True)
    async def watcher(self, message: Message):
        if not self._db.get("BurnSaver", "enabled", False):
            return

        if not self._is_burn(message):
            return

        try:
            import tempfile
            import os

            sender = self._get_sender_name(message)

            # Определяем расширение
            media = message.media
            if hasattr(media, 'document') and media.document:
                mime = media.document.mime_type or ""
                if "video" in mime:
                    ext = ".mp4"
                else:
                    ext = ".jpg"
            else:
                ext = ".jpg"

            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                tmp_path = tmp.name

            path = await message.download_media(tmp_path)
            if not path:
                return

            caption = self.strings("saved").format(sender)
            await self._client.send_file("me", path, caption=caption)
            os.unlink(path)
            self._saved += 1
            logger.info(f"BurnSaver: сохранено от {sender}")
        except Exception as e:
            logger.exception(e)

    @loader.command(
        ru_doc="— включить сохранение сгорающих фото/видео",
        en_doc="— enable burn media saving",
    )
    async def bson(self, message: Message):
        self._db.set("BurnSaver", "enabled", True)
        await utils.answer(message, self.strings("enabled"))

    @loader.command(
        ru_doc="— выключить сохранение",
        en_doc="— disable burn media saving",
    )
    async def bsoff(self, message: Message):
        self._db.set("BurnSaver", "enabled", False)
        await utils.answer(message, self.strings("disabled"))

    @loader.command(
        ru_doc="— статус",
        en_doc="— status",
    )
    async def bsstatus(self, message: Message):
        if self._db.get("BurnSaver", "enabled", False):
            await utils.answer(message, self.strings("status_on").format(self._saved))
        else:
            await utils.answer(message, self.strings("status_off"))
