# meta developer: @sotka_modules
# scope: heroku_only

__version__ = (3, 8, 8, 3)

import re
import time
from .. import loader, utils
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights


@loader.tds
class HAdmin(loader.Module):
    """Админ-команды (mute/ban/global) с флагами -u -t -r и поддержкой реплая"""

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

        "gmutet": "🌍🔇 {n} [<code>{i}</code>] глобально замучен {t}",
        "gbant": "🌍🚫 {n} [<code>{i}</code>] глобально забанен {t}",

        "gunmute": "🌍🔊 {n} [<code>{i}</code>] глобально размучен",
        "gunban": "🌍✅ {n} [<code>{i}</code>] глобально разбанен",
    }

    async def _parse_args(self, m):
        args = m.raw_text.split()[1:]

        user = None
        reason_parts = []
        time_parts = []

        reply = await m.get_reply_message()
        if reply and reply.sender:
            user = reply.sender

        i = 0
        while i < len(args):
            if args[i] == "-u" and i + 1 < len(args):
                user = args[i + 1]
                i += 2
                continue

            if args[i] == "-t" and i + 1 < len(args):
                time_parts.append(args[i + 1])
                i += 2
                continue

            if args[i] == "-r" and i + 1 < len(args):
                i += 1
                while i < len(args) and not args[i].startswith("-"):
                    reason_parts.append(args[i])
                    i += 1
                continue

            i += 1

        if isinstance(user, str):
            try:
                user = await m.client.get_entity(user)
            except Exception:
                user = None

        t = self._parse_time(time_parts)
        reason = " ".join(reason_parts)

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

        if d:
            parts.append(f"{d}д")
        if h:
            parts.append(f"{h}ч")
        if m:
            parts.append(f"{m}м")
        if s:
            parts.append(f"{s}с")

        return " ".join(parts)

    async def _apply(self, chat, user, **rights):
        if "until_date" not in rights:
            rights["until_date"] = 0

        await self.client(
            EditBannedRequest(
                chat,
                user.id,
                ChatBannedRights(**rights),
            )
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
        """-u user | reply -t время -r причина — мут"""
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

    async def haunmutecmd(self, m):
        """-u user | reply — снять мут"""
        user, _, _ = await self._parse_args(m)

        if not user:
            return await utils.answer(m, self.strings("no_user"))

        await self._apply(m.chat_id, user, send_messages=False)

        await utils.answer(
            m,
            self.strings("mute_off").format(n=user.first_name, i=user.id),
        )

    async def habancmd(self, m):
        """-u user | reply -t время -r причина — бан"""
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

    async def haunbancmd(self, m):
        """-u user | reply — снять бан"""
        user, _, _ = await self._parse_args(m)

        if not user:
            return await utils.answer(m, self.strings("no_user"))

        await self._apply(m.chat_id, user)

        await utils.answer(
            m,
            self.strings("ban_off").format(n=user.first_name, i=user.id),
        )

    async def hakickcmd(self, m):
        """-u user | reply — кик"""
        user, _, _ = await self._parse_args(m)

        if not user:
            return await utils.answer(m, self.strings("no_user"))

        await self._apply(m.chat_id, user, view_messages=True, until_date=1)

        await utils.answer(
            m,
            self.strings("kick").format(n=user.first_name, i=user.id),
        )

    async def hgmute(self, m):
        """-u user | reply — глобальный мут"""
        user, _, _ = await self._parse_args(m)

        if not user:
            return await utils.answer(m, self.strings("no_user"))

        await self._global(user, send_messages=True)

        await utils.answer(
            m,
            self.strings("gmute").format(n=user.first_name, i=user.id),
        )

    async def hgban(self, m):
        """-u user | reply — глобальный бан"""
        user, _, _ = await self._parse_args(m)

        if not user:
            return await utils.answer(m, self.strings("no_user"))

        await self._global(user, view_messages=True)

        await utils.answer(
            m,
            self.strings("gban").format(n=user.first_name, i=user.id),
        )

    async def hagmutecmd(self, m):
        """-u user | reply -t время -r причина — глобальный мут"""
        user, t, r = await self._parse_args(m)

        if not user:
            return await utils.answer(m, self.strings("no_user"))

        kw = {"send_messages": True}
        if t:
            kw["until_date"] = int(time.time()) + t

        await self._global(user, **kw)

        txt = self.strings("gmutet").format(
            n=user.first_name,
            i=user.id,
            t=self._format_time(t),
        )

        if r:
            txt += "\n" + self.strings("reason").format(r=r)

        await utils.answer(m, txt)

    async def hagbancmd(self, m):
        """-u user | reply -t время -r причина — глобальный бан"""
        user, t, r = await self._parse_args(m)

        if not user:
            return await utils.answer(m, self.strings("no_user"))

        kw = {"view_messages": True}
        if t:
            kw["until_date"] = int(time.time()) + t

        await self._global(user, **kw)

        txt = self.strings("gbant").format(
            n=user.first_name,
            i=user.id,
            t=self._format_time(t),
        )

        if r:
            txt += "\n" + self.strings("reason").format(r=r)

        await utils.answer(m, txt)

    async def hgunmutecmd(self, m):
        """-u user | reply — глобальный анмут"""
        user, _, _ = await self._parse_args(m)

        if not user:
            return await utils.answer(m, self.strings("no_user"))

        await self._global(user, send_messages=False)

        await utils.answer(
            m,
            self.strings("gunmute").format(n=user.first_name, i=user.id),
        )

    async def hgunbancmd(self, m):
        """-u user | reply — глобальный разбан"""
        user, _, _ = await self._parse_args(m)

        if not user:
            return await utils.answer(m, self.strings("no_user"))

        await self._global(user)

        await utils.answer(
            m,
            self.strings("gunban").format(n=user.first_name, i=user.id),
        )
