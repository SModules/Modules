# meta developer: @sotka_modules
# meta name: SMPays

from .. import loader, utils
import uuid
import urllib.parse
import aiohttp

__version__ = (1, 4, 2, 5)


@loader.tds
class SMPays(loader.Module):
    """
    SMPays

    Inline-модуль для создания TON-счетов:
    • TON (Tonkeeper / Tonhub / ton://)
    • TON через CryptoBot

    Payment ID используется как комментарий.
    """

    strings = {
        "name": "SMPays",
        "no_amount": "❌ <b>Укажи сумму в TON.</b>",
        "bad_amount": "❌ <b>Сумма должна быть числом больше 0.</b>",
        "cb_not_set": "❌ <b>CryptoBot токен не настроен.</b>",
        "cb_error": "❌ <b>Не удалось создать счёт CryptoBot.</b>",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "ton_address",
                "fowup.t.me",
                "TON DNS или адрес кошелька",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "cryptobot_token",
                "",
                "API-токен CryptoBot",
                validator=loader.validators.String(),
            ),
        )

    def _gen_payment_id(self):
        return uuid.uuid4().hex[:20].upper()

    def _build_qr(self, link: str):
        return (
            "https://api.qrserver.com/v1/create-qr-code/"
            "?size=600x600"
            "&margin=10"
            "&format=png"
            f"&data={urllib.parse.quote(link)}"
        )

    async def _create_cryptobot_invoice(self, ton_amount, payment_id):
        token = self.config["cryptobot_token"]
        if not token:
            return None

        url = "https://pay.crypt.bot/api/createInvoice"
        headers = {"Crypto-Pay-API-Token": token}
        data = {
            "asset": "TON",
            "amount": str(ton_amount),
            "description": f"SMPays | {payment_id}",
            "allow_comments": False,
            "allow_anonymous": True,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers) as r:
                    res = await r.json()

            if res.get("ok"):
                return res["result"]["pay_url"]
        except Exception:
            pass

        return None

    @loader.command(
        ru_doc="<сумма> — создать TON-счёт (TON / CryptoBot)",
    )
    async def smpaycmd(self, message):
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("no_amount"))
            return

        try:
            amount = float(args.replace(",", "."))
            if amount <= 0:
                raise ValueError
        except ValueError:
            await utils.answer(message, self.strings("bad_amount"))
            return

        payment_id = self._gen_payment_id()
        nano = int(amount * 1_000_000_000)

        address = self.config["ton_address"]
        ton_link = f"ton://transfer/{address}?amount={nano}&text={payment_id}"
        qr_url = self._build_qr(ton_link)

        text = (
            f"<b>💸 SMPays</b>\n\n"
            f"💎 <b>Сумма:</b> <code>{amount} TON</code>\n"
            f"👛 <b>TON адрес:</b>\n<code>{address}</code>\n\n"
            f"📝 <b>Payment ID:</b>\n<code>{payment_id}</code>\n\n"
            f"❗ Используйте Payment ID как комментарий"
        )

        markup = [
            [
                {
                    "text": "💎 Tonkeeper",
                    "url": f"https://app.tonkeeper.com/transfer/{address}"
                           f"?amount={nano}&text={payment_id}",
                },
                {
                    "text": "💎 Tonhub",
                    "url": f"https://tonhub.com/transfer/{address}"
                           f"?amount={nano}&text={payment_id}",
                },
            ],
            [
                {
                    "text": "💎 Other",
                    "url": ton_link,
                }
            ],
            [
                {
                    "text": "📋 Copy Address",
                    "copy": address,
                },
                {
                    "text": "📋 Copy Payment ID",
                    "copy": payment_id,
                },
            ],
            [
                {
                    "text": "📷 QR",
                    "url": qr_url,
                }
            ],
        ]

        # CryptoBot TON
        if self.config["cryptobot_token"]:
            cb_link = await self._create_cryptobot_invoice(amount, payment_id)
            if cb_link:
                markup.append(
                    [
                        {
                            "text": "🤖 CryptoBot (TON)",
                            "url": cb_link,
                        }
                    ]
                )

        await self.inline.form(
            text=text,
            message=message,
            reply_markup=markup,
        )


