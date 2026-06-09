from __future__ import annotations

import asyncio
import logging

import discord
from discord.ext import commands

from shorts_bot.briefing.builder import build_morning_briefing
from shorts_bot.config import settings
from shorts_bot.services.ops import BotOperations

log = logging.getLogger(__name__)


def _chunk(text: str, limit: int = 1900) -> list[str]:
    if len(text) <= limit:
        return [text]
    parts: list[str] = []
    while text:
        parts.append(text[:limit])
        text = text[limit:]
    return parts


class ShortsDiscordBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.dm_messages = True
        super().__init__(command_prefix=settings.discord_command_prefix, intents=intents)
        self.ops = BotOperations()
        self._briefing_sent = False

    async def setup_hook(self) -> None:
        await self.add_cog(ShortsCog(self))

    async def on_ready(self) -> None:
        log.info("Discord bot ready as %s", self.user)
        if settings.discord_send_briefing_on_start and not self._briefing_sent:
            self._briefing_sent = True
            await self._send_briefing()

    async def _send_briefing(self) -> None:
        text = build_morning_briefing()
        for user_id in settings.discord_notify_list:
            if not user_id.isdigit():
                log.warning(
                    "DISCORD_OWNER_ID must be a numeric user ID, not a username (%s). "
                    "See docs/MORNING.md — Developer Mode → Copy User ID.",
                    user_id[:20],
                )
                continue
            try:
                user = await self.fetch_user(int(user_id))
                for part in _chunk(text):
                    await user.send(part)
            except Exception as exc:  # noqa: BLE001
                log.warning("Could not DM %s: %s", user_id, exc)


class ShortsCog(commands.Cog):
    def __init__(self, bot: ShortsDiscordBot) -> None:
        self.bot = bot
        self.ops = bot.ops

    @commands.command(name="help")
    async def help_cmd(self, ctx: commands.Context) -> None:
        await ctx.reply(
            "**Shorts Bot commands**\n"
            "`!status` — system status\n"
            "`!chat <message>` — talk to the strategist\n"
            "`!draft <topic>` — create a script draft\n"
            "`!pending` — list improvements & drafts\n"
            "`!yes <id>` / `!no <id>` — approve/skip improvement\n"
            "`!draftyes <id>` / `!draftno <id> [reason]` — draft decisions\n"
            "`!sync` — YouTube Analytics sync\n"
            "`!dev <title> | <description>` — queue a dev/coding task\n"
            "`!devpending` — list dev tasks\n"
            "`!devyes <id>` / `!devno <id>` — dev task decisions\n"
            "`!briefing` — morning checklist again\n"
            "`!myid` — your numeric user ID (for morning auto-DMs)"
        )

    @commands.command(name="myid")
    async def myid_cmd(self, ctx: commands.Context) -> None:
        uid = ctx.author.id
        await ctx.reply(
            f"Your Discord user ID: `{uid}`\n\n"
            f"Paste into `.env`:\n"
            f"`DISCORD_OWNER_ID={uid}`\n\n"
            f"Then restart the bot — it can auto-DM you the morning briefing on startup."
        )

    @commands.command(name="status")
    async def status_cmd(self, ctx: commands.Context) -> None:
        s = self.ops.status()
        yt = s["youtube"]
        msg = (
            f"**Status**\n"
            f"Chat: {'full' if s['openai'] else 'offline'}\n"
            f"YouTube: {'ready' if yt.get('ready') else 'needs setup'}\n"
            f"Pending improvements: {s['pending_improvements']}\n"
            f"Pending drafts: {s['pending_drafts']}\n"
            f"Pending dev tasks: {s['pending_dev']}\n"
            f"Web: http://localhost:{settings.web_port}"
        )
        await ctx.reply(msg)

    @commands.command(name="chat")
    async def chat_cmd(self, ctx: commands.Context, *, message: str) -> None:
        async with ctx.typing():
            reply = await asyncio.to_thread(self.ops.chat, message)
        for part in _chunk(reply):
            await ctx.reply(part)

    @commands.command(name="draft")
    async def draft_cmd(self, ctx: commands.Context, *, topic: str) -> None:
        msg = await asyncio.to_thread(self.ops.create_draft, topic)
        await ctx.reply(msg)

    @commands.command(name="pending")
    async def pending_cmd(self, ctx: commands.Context) -> None:
        imps = self.ops.list_improvements()
        drafts = self.ops.list_drafts()
        lines = ["**Pending improvements**"]
        if imps:
            for i in imps[:8]:
                lines.append(f"#{i['id']} [{i['category']}] {i['title']}")
        else:
            lines.append("(none)")
        lines.append("\n**Pending drafts**")
        if drafts:
            for d in drafts[:8]:
                lines.append(f"#{d['id']} {d['topic']}")
        else:
            lines.append("(none)")
        await ctx.reply("\n".join(lines))

    @commands.command(name="yes")
    async def yes_cmd(self, ctx: commands.Context, imp_id: int) -> None:
        msg = await asyncio.to_thread(self.ops.approve_improvement, imp_id)
        await ctx.reply(msg)

    @commands.command(name="no")
    async def no_cmd(self, ctx: commands.Context, imp_id: int) -> None:
        msg = await asyncio.to_thread(self.ops.reject_improvement, imp_id)
        await ctx.reply(msg)

    @commands.command(name="draftyes")
    async def draft_yes(self, ctx: commands.Context, draft_id: int) -> None:
        msg = await asyncio.to_thread(self.ops.approve_draft, draft_id)
        await ctx.reply(msg)

    @commands.command(name="draftno")
    async def draft_no(self, ctx: commands.Context, draft_id: int, *, reason: str = "Rejected.") -> None:
        msg = await asyncio.to_thread(self.ops.reject_draft, draft_id, reason)
        await ctx.reply(msg)

    @commands.command(name="sync")
    async def sync_cmd(self, ctx: commands.Context) -> None:
        result = await asyncio.to_thread(self.ops.youtube_sync)
        await ctx.reply(result.get("message", "Done"))

    @commands.command(name="dev")
    async def dev_cmd(self, ctx: commands.Context, *, payload: str) -> None:
        if "|" in payload:
            title, desc = payload.split("|", 1)
        else:
            title, desc = payload[:80], payload
        msg = await asyncio.to_thread(self.ops.create_dev_task, title.strip(), desc.strip())
        await ctx.reply(msg)

    @commands.command(name="devpending")
    async def dev_pending(self, ctx: commands.Context) -> None:
        tasks = self.ops.list_dev_tasks()
        if not tasks:
            await ctx.reply("No pending dev tasks.")
            return
        lines = ["**Dev tasks (Yes/No in web UI too)**"]
        for t in tasks[:8]:
            lines.append(f"#{t['id']} {t['title']}")
        await ctx.reply("\n".join(lines))

    @commands.command(name="devyes")
    async def dev_yes(self, ctx: commands.Context, task_id: int) -> None:
        msg = await asyncio.to_thread(self.ops.approve_dev_task, task_id)
        await ctx.reply(msg)

    @commands.command(name="devno")
    async def dev_no(self, ctx: commands.Context, task_id: int) -> None:
        msg = await asyncio.to_thread(self.ops.reject_dev_task, task_id)
        await ctx.reply(msg)

    @commands.command(name="briefing")
    async def briefing_cmd(self, ctx: commands.Context) -> None:
        text = build_morning_briefing()
        for part in _chunk(text):
            await ctx.reply(part)


def run_bot() -> None:
    if not settings.has_discord:
        raise SystemExit(
            "DISCORD_BOT_TOKEN missing in .env\n"
            "Discord Developer Portal → Bot → Reset Token → paste in .env\n"
            "(Public key is already saved — you need the bot token to connect.)"
        )
    bot = ShortsDiscordBot()
    bot.run(settings.discord_bot_token)
