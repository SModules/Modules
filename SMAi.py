# meta developer: @sotka_modules
# meta name: SMai

from .. import loader, utils
import aiohttp

__version__ = (1, 2, 0, 0)

API_URL = "https://api.onlysq.ru/ai/openai/chat/completions"
API_KEY = "openai"


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

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "user", "content": text}
            ]
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(API_URL, headers=headers, json=payload) as resp:
                    data = await resp.json()

            answer = data["choices"][0]["message"]["content"]
            await message.edit(answer[:4000])

        except Exception as e:
            await message.edit(f"Error: {e}")
