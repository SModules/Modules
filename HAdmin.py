# meta developer: @sova_modules
# scope: heroku_only

import re
import time
from .. import loader, utils
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights


@loader.tds
class HAdmin(loader.Module):
    strings = {
        "name": "HAdmin",

        "no_user": "❌ Пользователь не найден",
        "no_rights": "❌ Недостаточно прав",

        "forever": "навсегда",
        "reason": "📄 Причина: {r}",

        "mute_on": "🔇 {n} [<code>{i}</code>] замучен {t}",
        "mute_off": "🔊 {n} [<code>{i}</code>] размучен",

        "ban_on": "🚫 {n} [<code>{i}</code>] забанен {t}",
        "ban_off": "✅ {n} [<code>{i}</code>] разбанен",

        "kick": "👢 {n} [<code>{i}</code>] кикнут",
    }

    async def _target(self, m, args):
        r = await m.get_reply_message()
        if r:
            return r.sender, args

        if not args:
            return None, args

        try:
            return await m.client.get_entity(args[0]), args[1:]
        except Exception:
            return None, args

    def _parse_time(self, args):
        if not args:
            return None

        m = re.match(r"(\d+)([smhd])", args[0])
        if not m:
            return None

        v, u = int(m.group(1)), m.group(2)
        return v * {"s": 1, "m": 60, "h": 3600, "d": 86400}[u]

    async def _apply(self, m, u, **rights):
        await m.client(
            EditBannedRequest(
                m.chat_id,
                u.id,
                ChatBannedRights(**rights),
            )
        )

    async def hamutecmd(self, m):
        args = m.raw_text.split()[1:]
        u, args = await self._target(m, args)
        if not u:
            return await utils.answer(m, self.strings("no_user"))

        t = self._parse_time(args)
        r = " ".join(a for a in args if not re.match(r"\d+[smhd]", a))

        kw = {"send_messages": True}
        if t:
            kw["until_date"] = int(time.time()) + t

        await self._apply(m, u, **kw)

        txt = self.strings("mute_on").format(
            n=u.first_name,
            i=u.id,
            t=utils.format_timedelta(t) if t else self.strings("forever"),
        )

        if r:
            txt += "\n" + self.strings("reason").format(r=r)

        await utils.answer(m, txt)

    async def haunmutecmd(self, m):
        args = m.raw_text.split()[1:]
        u, _ = await self._target(m, args)
        if not u:
            return await utils.answer(m, self.strings("no_user"))

        await self._apply(m, u, send_messages=False)

        await utils.answer(
            m,
            self.strings("mute_off").format(n=u.first_name, i=u.id),
        )

    async def habancmd(self, m):
        args = m.raw_text.split()[1:]
        u, args = await self._target(m, args)
        if not u:
            return await utils.answer(m, self.strings("no_user"))

        t = self._parse_time(args)
        r = " ".join(a for a in args if not re.match(r"\d+[smhd]", a))

        kw = {"view_messages": True}
        if t:
            kw["until_date"] = int(time.time()) + t

        await self._apply(m, u, **kw)

        txt = self.strings("ban_on").format(
            n=u.first_name,
            i=u.id,
            t=utils.format_timedelta(t) if t else self.strings("forever"),
        )

        if r:
            txt += "\n" + self.strings("reason").format(r=r)

        await utils.answer(m, txt)

    async def haunbancmd(self, m):
        args = m.raw_text.split()[1:]
        u, _ = await self._target(m, args)
        if not u:
            return await utils.answer(m, self.strings("no_user"))

        await self._apply(m, u)

        await utils.answer(
            m,
            self.strings("ban_off").format(n=u.first_name, i=u.id),
        )

    async def hakickcmd(self, m):
        args = m.raw_text.split()[1:]
        u, _ = await self._target(m, args)
        if not u:
            return await utils.answer(m, self.strings("no_user"))

        await self._apply(m, u, view_messages=True, until_date=1)

        await utils.answer(
            m,
            self.strings("kick").format(n=u.first_name, i=u.id),
        )
