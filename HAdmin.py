# meta developer: @sotka_modules
# scope: heroku_only

__version__ = (3, 8, 8, 2)

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

        "forever": "навсегда",
        "reason": "📄 Причина: {r}",

        "mute_on": "🔇 {n} [<code>{i}</code>] замучен {t}",
        "mute_off": "🔊 {n} [<code>{i}</code>] размучен",

        "ban_on": "🚫 {n} [<code>{i}</code>] забанен {t}",
        "ban_off": "✅ {n} [<code>{i}</code>] разбанен",

        "kick": "👢 {n} [<code>{i}</code>] кикнут",

        "gmute": "🌍🔇 {n} [<code>{i}</code>] глобально замучен",
        "gban": "🌍🚫 {n} [<code>{i}</code>] глобально забанен",

        "gunmute": "🌍🔊 {n} [<code>{i}</code>] глобально размучен",
        "gunban": "🌍✅ {n} [<code>{i}</code>] глобально разбанен",
    }

    async def _parse_args(self, m):
        args = m.raw_text.split()[1:]

        user = None
        reason = ""
        time_args = []

        reply = await m.get_reply_message()
        if reply and reply.sender:
            user = reply.sender

        i = 0
        while i < len(args):
            if args[i] == "-u":
                i += 1
                user = args[i]
            elif args[i] == "-r":
                i += 1
                reason = args[i]
            elif args[i] == "-t":
                i += 1
                time_args.append(args[i])
            i += 1

        if isinstance(user, str):
            try:
                user = await m.client.get_entity(user)
            except Exception:
                user = None

        t = self._parse_time(time_args)

        return user, t, reason

    def _parse_time(self, args):
        if not args:
            return None

        total = 0
        for part in args:
            for v, u in re.findall(r"(\d+)([smhd])", part):
                total += int(v) * {"s": 1, "m": 60, "h": 3600, "d": 86400}[u]

        return total if total else None

    def _format_time(self, seconds):
        if not seconds:
            return self.strings("forever")

        parts = []
        d = seconds // 86400
        seconds %= 86400
        h = seconds // 3600
        seconds %= 3600
        m = seconds // 60
        s = seconds % 60

        if d: parts.append(f"{d}д")
        if h: parts.append(f"{h}ч")
        if m: parts.append(f"{m}м")
        if s: parts.append(f"{s}с")

        return " ".join(parts)

    async def _apply(self, chat, user, **rights):
        if "until_date" not in rights:
            rights["until_date"] = 0

        await self.client(
            EditBannedRequest(chat, user.id, ChatBannedRights(**rights))
        )

    async def _global(self, user, **rights):
        dialogs = await self.client.get_dialogs(limit=None)

        for d in dialogs:
            if not d.is_group and not d.is_channel:
                continue

            try:
                perms = await self.client.get_permissions(d.entity, "me")
                if not perms.is_admin:
                    continue

                await self._apply(d.entity, user, **rights)
            except Exception:
                continue

    async def hamutecmd(self, m):
        user, t, r = await self._parse_args(m)
        if not user:
            return await utils.answer(m, self.strings("no_user"))

        kw = {"send_messages": True}
        if t:
            kw["until_date"] = int(time.time()) + t

        await self._apply(m.chat_id, user, **kw)

        txt = self.strings("mute_on").format(
            n=user.first_name,
            i=user.id,
            t=self._format_time(t),
        )

        if r:
            txt += "\n" + self.strings("reason").format(r=r)

        await utils.answer(m, txt)

    async def habancmd(self, m):
        user, t, r = await self._parse_args(m)
        if not user:
            return await utils.answer(m, self.strings("no_user"))

        kw = {"view_messages": True}
        if t:
            kw["until_date"] = int(time.time()) + t

        await self._apply(m.chat_id, user, **kw)

        txt = self.strings("ban_on").format(
            n=user.first_name,
            i=user.id,
            t=self._format_time(t),
        )

        if r:
            txt += "\n" + self.strings("reason").format(r=r)

        await utils.answer(m, txt)

    async def hagmutecmd(self, m):
        user, t, r = await self._parse_args(m)
        if not user:
            return await utils.answer(m, self.strings("no_user"))

        kw = {"send_messages": True}
        if t:
            kw["until_date"] = int(time.time()) + t

        await self._global(user, **kw)

        txt = f"🌍🔇 {user.first_name} [<code>{user.id}</code>] глобально замучен {self._format_time(t)}"

        if r:
            txt += "\n" + self.strings("reason").format(r=r)

        await utils.answer(m, txt)

    async def hagbancmd(self, m):
        user, t, r = await self._parse_args(m)
        if not user:
            return await utils.answer(m, self.strings("no_user"))

        kw = {"view_messages": True}
        if t:
            kw["until_date"] = int(time.time()) + t

        await self._global(user, **kw)

        txt = f"🌍🚫 {user.first_name} [<code>{user.id}</code>] глобально забанен {self._format_time(t)}"

        if r:
            txt += "\n" + self.strings("reason").format(r=r)

        await utils.answer(m, txt)
