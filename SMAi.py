# meta developer: @sotka_modules
# meta name: SMai

from .. import loader, utils
import aiohttp

__version__ = (1, 0, 0, 0)

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"


@loader.tds
class SMai(loader.Module):
    """
    SMai
    """

    strings = {
        "name": "SMai"
    }

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

        payload = {
            "inputs": text,
            "parameters": {
                "max_new_tokens": 400,
                "temperature": 0.7
            }
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(API_URL, json=payload) as resp:
                    data = await resp.json()

            if isinstance(data, list):
                answer = data[0]["generated_text"]
            else:
                answer = str(data)

            await message.edit(answer[:4000])

        except Exception as e:
            await message.edit(f"Error: {e}")
