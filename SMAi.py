# meta developer: @sotka_modules
# meta name: SMai

from .. import loader, utils
import aiohttp
import base64
import io

__version__ = (1, 6, 0, 0)

API_KEY = "openai"

CHAT_URL = "https://api.onlysq.ru/ai/openai/chat/completions"
IMG_URL = "https://api.onlysq.ru/ai/imagen"

UPLOAD_URL = "https://cloud.onlysq.ru/upload"
FILE_URL = "https://cloud.onlysq.ru/file"
DELETE_URL = "https://cloud.onlysq.ru/delete"


@loader.tds
class SMai(loader.Module):
    """
    SMai
    """

    strings = {"name": "SMai"}

    async def smaicmd(self, message):
        """
        <text or reply>
        """
        text = utils.get_args_raw(message)

        if not text:
            reply = await message.get_reply_message()
            if reply:
                text = reply.raw_text

        if not text:
            return await utils.answer(message, "Write something")

        await message.edit("🤖 thinking...")

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "gpt-5",
            "messages": [{"role": "user", "content": text}]
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(CHAT_URL, headers=headers, json=payload) as resp:
                    data = await resp.json(content_type=None)

            if "choices" not in data:
                return await message.edit(str(data)[:3000])

            answer = data["choices"][0]["message"]["content"]
            await message.edit(answer[:4000])

        except Exception as e:
            await message.edit(f"Error: {e}")

    async def smimgcmd(self, message):
        """
        <prompt>
        """
        prompt = utils.get_args_raw(message)

        if not prompt:
            return await utils.answer(message, "Write prompt")

        await message.edit("🎨 generating image...")

        headers = {"Authorization": f"Bearer {API_KEY}"}

        payload = {
            "model": "flux-2-dev",
            "prompt": prompt,
            "ratio": "16:9"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(IMG_URL, headers=headers, json=payload) as resp:
                    data = await resp.json(content_type=None)

            if "files" not in data:
                return await message.edit(str(data)[:3000])

            img_data = base64.b64decode(data["files"][0])
            file = io.BytesIO(img_data)
            file.name = "image.png"

            await message.delete()
            await message.respond(file=file)

        except Exception as e:
            await message.edit(f"Error: {e}")

    async def smuploadcmd(self, message):
        """
        reply file
        """
        reply = await message.get_reply_message()
        if not reply or not reply.file:
            return await utils.answer(message, "Reply to file")

        await message.edit("📤 uploading...")

        file_bytes = await reply.download_media(bytes)
        filename = reply.file.name or "file.bin"

        try:
            data = aiohttp.FormData()
            data.add_field(
                "file",
                file_bytes,
                filename=filename,
                content_type="application/octet-stream"
            )

            async with aiohttp.ClientSession() as session:
                async with session.post(UPLOAD_URL, data=data) as resp:
                    result = await resp.json(content_type=None)

            if result.get("ok"):
                await message.edit(
                    f"✅ Uploaded\n🔗 {result.get('url')}\n🔑 Owner: {result.get('owner')}"
                )
            else:
                await message.edit(str(result))

        except Exception as e:
            await message.edit(f"Error: {e}")

    async def smdownloadcmd(self, message):
        """
        <fileid or link>
        """
        arg = utils.get_args_raw(message)

        if not arg:
            return await utils.answer(message, "Write file id or link")

        if "cloud.onlysq.ru" in arg:
            arg = arg.rstrip("/").split("/")[-1]

        await message.edit("📥 downloading...")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{FILE_URL}/{arg}") as resp:
                    data = await resp.read()
                    filename = resp.headers.get(
                        "Content-Disposition",
                        "file.bin"
                    ).split("filename=")[-1]

            file = io.BytesIO(data)
            file.name = filename.strip('"')

            await message.delete()
            await message.respond(file=file)

        except Exception as e:
            await message.edit(f"Error: {e}")

    async def smdeletecmd(self, message):
        """
        <fileid or link> <ownerkey>
        """
        args = utils.get_args_raw(message).split()

        if len(args) < 2:
            return await utils.answer(message, "Write fileid/link and ownerkey")

        fileid = args[0]
        ownerkey = args[1]

        if "cloud.onlysq.ru" in fileid:
            fileid = fileid.rstrip("/").split("/")[-1]

        headers = {"Authorization": ownerkey}

        await message.edit("🗑 deleting...")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{DELETE_URL}/{fileid}",
                    headers=headers
                ) as resp:
                    result = await resp.json(content_type=None)

            if result.get("ok"):
                await message.edit("✅ Deleted")
            else:
                await message.edit(str(result))

        except Exception as e:
            await message.edit(f"Error: {e}")
