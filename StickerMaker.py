"""
    🎨 StickerMaker - Создаёт стикеры из фото и добавляет в стикерпак

    Ответь на фото командой .st — добавит стикер в выбранный пак.
    .st 30 — добавит 30 одинаковых стикеров из одного фото.
    Поддерживает выбор существующего пака или создание нового.
"""

version = (1, 1, 0)

# meta developer: @sotka_modules
# meta banner: https://x0.at/oTzv.png
# scope: hikka_only
# requires: Pillow

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
from herokutl.tl.functions.stickers import (
    CreateStickerSetRequest,
    AddStickerToSetRequest,
)
from herokutl.tl.types import InputStickerSetItem
from herokutl.tl.functions.messages import GetAllStickersRequest
from herokutl.tl.types import InputStickerSetShortName
import logging
import io
import asyncio
import os
import tempfile

logger = logging.getLogger(__name__)

STICKER_SIZE = 512


def _crop_to_square(img):
    from PIL import Image
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    return img.crop((left, top, left + side, top + side)).resize(
        (STICKER_SIZE, STICKER_SIZE), Image.LANCZOS
    )


def _to_webp(img) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="WEBP", quality=95)
    buf.seek(0)
    return buf.read()


@loader.tds
class StickerMakerMod(loader.Module):
    """Создаёт стикеры из фото и добавляет в стикерпак"""

    version = (1, 1, 0)

    strings = {
        "name": "StickerMaker",
        "no_reply": "❌ Ответь на фото.",
        "no_photo": "❌ Это не фото.",
        "processing": "⏳ Обрабатываю фото...",
        "no_packs": "📭 Нет стикерпаков созданных через этот модуль.\nСоздай через <code>.stnew название</code>",
        "creating_pack": "✨ Создаю стикерпак <code>{}</code>...",
        "adding": "➕ Добавляю стикер <code>{}</code> / <code>{}</code>...",
        "done": "✅ <b>Готово!</b> Добавлено: <code>{}</code>\nПак: t.me/addstickers/{}",
        "pack_created": "✅ Стикерпак <b>{}</b> создан!\n🔗 t.me/addstickers/{}",
        "no_pack_selected": "❌ Сначала выбери пак через <code>.stpack</code> или создай через <code>.stnew название</code>",
        "error": "❌ Ошибка: <code>{}</code>",
        "pack_set": "✅ Активный пак: <code>{}</code>",
    }

    strings_ru = {
        "no_reply": "❌ Ответь на фото.",
        "no_photo": "❌ Это не фото.",
        "processing": "⏳ Обрабатываю фото...",
        "no_packs": "📭 Нет стикерпаков созданных через этот модуль.\nСоздай через <code>.stnew название</code>",
        "creating_pack": "✨ Создаю стикерпак <code>{}</code>...",
        "adding": "➕ Добавляю стикер <code>{}</code> / <code>{}</code>...",
        "done": "✅ <b>Готово!</b> Добавлено: <code>{}</code>\nПак: t.me/addstickers/{}",
        "pack_created": "✅ Стикерпак <b>{}</b> создан!\n🔗 t.me/addstickers/{}",
        "no_pack_selected": "❌ Сначала выбери пак через <code>.stpack</code> или создай через <code>.stnew название</code>",
        "error": "❌ Ошибка: <code>{}</code>",
        "pack_set": "✅ Активный пак: <code>{}</code>",
    }

    def __init__(self):
        self._db = None
        self._client = None

    async def client_ready(self, client, db):
        self._client = client
        self._db = db

    def _get_active_pack(self):
        return self._db.get("StickerMaker", "active_pack", None)

    def _set_active_pack(self, short_name: str):
        self._db.set("StickerMaker", "active_pack", short_name)

    def _get_my_packs(self):
        return self._db.get("StickerMaker", "my_packs", [])

    def _add_my_pack(self, short_name: str, title: str):
        packs = self._get_my_packs()
        packs.append({"short_name": short_name, "title": title})
        self._db.set("StickerMaker", "my_packs", packs)

    async def _upload_webp(self, webp_bytes: bytes):
        from herokutl.tl.types import DocumentAttributeSticker, InputStickerSetEmpty, InputDocument
        import io

        buf = io.BytesIO(webp_bytes)
        buf.name = "sticker.webp"

        msg = await self._client.send_file(
            "me",
            buf,
            attributes=[DocumentAttributeSticker(
                alt="🎨",
                stickerset=InputStickerSetEmpty()
            )],
            mime_type="image/webp",
            force_document=False,
        )
        doc = msg.document
        await msg.delete()
        return InputDocument(
            id=doc.id,
            access_hash=doc.access_hash,
            file_reference=doc.file_reference,
        )

    async def _prepare_webp(self, reply) -> bytes:
        from PIL import Image
        data = await reply.download_media(bytes)
        img = Image.open(io.BytesIO(data)).convert("RGBA")
        img = _crop_to_square(img)
        return _to_webp(img)

    @loader.command(
        ru_doc="[кол-во] — добавить стикер из фото в активный пак (ответь на фото)",
        en_doc="[count] — add sticker from photo to active pack (reply to photo)",
    )
    async def st(self, message: Message):
        reply = await message.get_reply_message()
        if not reply:
            await utils.answer(message, self.strings("no_reply"))
            return

        if not (reply.photo or (reply.document and "image" in (reply.document.mime_type or ""))):
            await utils.answer(message, self.strings("no_photo"))
            return

        active_pack = self._get_active_pack()
        if not active_pack:
            await utils.answer(message, self.strings("no_pack_selected"))
            return

        args = utils.get_args_raw(message).strip()
        count = 1
        if args.isdigit():
            count = max(1, min(int(args), 120))

        await utils.answer(message, self.strings("processing"))

        try:
            webp_bytes = await self._prepare_webp(reply)

            for i in range(1, count + 1):
                await utils.answer(message, self.strings("adding").format(i, count))
                try:
                    file = await self._upload_webp(webp_bytes)
                    await self._client(AddStickerToSetRequest(
                        stickerset=InputStickerSetShortName(short_name=active_pack),
                        sticker=InputStickerSetItem(
                            document=file,
                            emoji="🎨"
                        )
                    ))
                except Exception as e:
                    logger.exception(e)
                    await utils.answer(message, self.strings("error").format(utils.escape_html(str(e))))
                    return
                if count > 1:
                    await asyncio.sleep(0.5)

            await utils.answer(message, self.strings("done").format(count, active_pack))

        except Exception as e:
            logger.exception(e)
            await utils.answer(message, self.strings("error").format(utils.escape_html(str(e))))

    @loader.command(
        ru_doc="<название> — создать новый стикерпак",
        en_doc="<title> — create new sticker pack",
    )
    async def stnew(self, message: Message):
        args = utils.get_args_raw(message).strip()
        if not args:
            await utils.answer(message, "❌ Укажи название: <code>.stnew Мой пак</code>")
            return

        reply = await message.get_reply_message()
        if not reply or not (reply.photo or (reply.document and "image" in (reply.document.mime_type or ""))):
            await utils.answer(message, "❌ Ответь на фото — оно станет первым стикером в паке.")
            return

        await utils.answer(message, self.strings("creating_pack").format(args))

        try:
            from PIL import Image

            me = await self._client.get_me()
            short_name = f"sm{me.id}_{int(asyncio.get_event_loop().time())}_by_{me.username or me.id}"

            webp_bytes = await self._prepare_webp(reply)
            file = await self._upload_webp(webp_bytes)

            await self._client(CreateStickerSetRequest(
                user_id=me.id,
                title=args,
                short_name=short_name,
                stickers=[InputStickerSetItem(
                    document=file,
                    emoji="🎨"
                )]
            ))

            self._set_active_pack(short_name)
            self._add_my_pack(short_name, args)

            await utils.answer(message, self.strings("pack_created").format(args, short_name))

        except Exception as e:
            logger.exception(e)
            await utils.answer(message, self.strings("error").format(utils.escape_html(str(e))))

    @loader.command(
        ru_doc="— показать стикерпаки созданные через этот модуль",
        en_doc="— show sticker packs created via this module",
    )
    async def stpack(self, message: Message):
        packs = self._get_my_packs()
        if not packs:
            await utils.answer(message, self.strings("no_packs"))
            return

        active = self._get_active_pack()
        lines = ["📦 <b>Мои стикерпаки:</b>\n"]
        for i, p in enumerate(packs, 1):
            check = " ✅" if p["short_name"] == active else ""
            lines.append(
                f"{i}. <b>{utils.escape_html(p['title'])}</b>{check}\n"
                f"   <code>.stset {utils.escape_html(p['short_name'])}</code>"
            )

        await utils.answer(message, "\n".join(lines))

    @loader.command(
        ru_doc="<short_name> — установить активный стикерпак",
        en_doc="<short_name> — set active sticker pack",
    )
    async def stset(self, message: Message):
        args = utils.get_args_raw(message).strip()
        if not args:
            await utils.answer(message, "❌ Укажи short_name: <code>.stset short_name</code>")
            return

        self._set_active_pack(args)
        await utils.answer(message, self.strings("pack_set").format(args))
