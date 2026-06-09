from __future__ import annotations

import asyncio
import logging

import datetime

import discord
from discord import app_commands
from discord.ext import commands, tasks

from shorts_bot.__version__ import __version__
from shorts_bot.briefing.builder import build_morning_briefing
from shorts_bot.config import settings
from shorts_bot.discord_bot.embeds import pending_embed, status_embed
from shorts_bot.discord_bot.notify import dm_all, notify_pending_summary
from shorts_bot.discord_bot.prefs import (
    briefing_already_sent_today,
    mark_briefing_sent_today,
    remember_dm_user,
)
from shorts_bot.learning.learned_file import LearnedFile
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
        super().__init__(
            command_prefix=settings.discord_command_prefix,
            intents=intents,
            help_command=None,
        )
        self.ops = BotOperations()
        self._briefing_sent = False

    async def setup_hook(self) -> None:
        cog = ShortsCog(self)
        await self.add_cog(cog)
        cog.morning_briefing.start()
        try:
            await self.tree.sync()
        except Exception as exc:  # noqa: BLE001
            log.warning("Slash command sync failed: %s", exc)

    async def on_ready(self) -> None:
        log.info("Discord bot ready as %s (v%s)", self.user, __version__)
        if settings.discord_send_briefing_on_start and not self._briefing_sent:
            self._briefing_sent = True
            await self._send_briefing()
            await notify_pending_summary(self, self.ops)

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        if isinstance(message.channel, discord.DMChannel):
            remember_dm_user(message.author.id)
        if (
            isinstance(message.channel, discord.DMChannel)
            and message.content
            and not message.content.strip().startswith(settings.discord_command_prefix)
        ):
            async with message.channel.typing():
                reply = await asyncio.to_thread(self.ops.chat, message.content.strip())
            for part in _chunk(reply):
                await message.channel.send(part)
            return
        await self.process_commands(message)

    async def _send_briefing(self) -> None:
        text = build_morning_briefing()
        n = await dm_all(self, text)
        if n:
            mark_briefing_sent_today()
            log.info("Briefing sent to %s user(s)", n)


class ShortsCog(commands.Cog):
    def __init__(self, bot: ShortsDiscordBot) -> None:
        self.bot = bot
        self.ops = bot.ops

    def cog_unload(self) -> None:
        self.morning_briefing.cancel()

    @tasks.loop(time=datetime.time(hour=settings.discord_briefing_hour, minute=settings.discord_briefing_minute))
    async def morning_briefing(self) -> None:
        await self.bot.wait_until_ready()
        if briefing_already_sent_today():
            return
        await self.bot._send_briefing()
        await notify_pending_summary(self.bot, self.ops)

    @morning_briefing.before_loop
    async def before_morning(self) -> None:
        await self.bot.wait_until_ready()

    async def _remember(self, ctx: commands.Context) -> None:
        if isinstance(ctx.channel, discord.DMChannel):
            remember_dm_user(ctx.author.id)

    @commands.command(name="help")
    async def help_cmd(self, ctx: commands.Context) -> None:
        await self._remember(ctx)
        await ctx.reply(
            "**Shorts Bot** — prefix `!` in servers. In **DMs**, just type normally.\n\n"
            "`!status` · `!chat <msg>` · `!draft <topic>` · `!pending`\n"
            "`!yes <id>` / `!no <id>` · `!draftyes` / `!draftno`\n"
            "`!sync` · `!applybrand` · `!produce` · `!dev title | desc` · `!devpending` · `!devyes` / `!devno`\n"
            "`!briefing` · `!learned` · `!rewards` · `!ping` · `!myid`\n"
            "Slash: `/status` `/draft` `/pending` `/briefing`"
        )

    @commands.command(name="ping")
    async def ping_cmd(self, ctx: commands.Context) -> None:
        await self._remember(ctx)
        lat = round(self.bot.latency * 1000)
        await ctx.reply(f"Pong — {lat}ms · v{__version__}")

    @commands.command(name="myid")
    async def myid_cmd(self, ctx: commands.Context) -> None:
        await self._remember(ctx)
        uid = ctx.author.id
        await ctx.reply(
            f"Your user ID: `{uid}`\n"
            f"Optional `.env`: `DISCORD_OWNER_ID={uid}`\n"
            f"(Bot already remembers your DM for briefings.)"
        )

    @commands.command(name="learned")
    async def learned_cmd(self, ctx: commands.Context) -> None:
        await self._remember(ctx)
        text = LearnedFile(settings.learned_path).read_tail(1500)
        for part in _chunk(text):
            await ctx.reply(part)

    @commands.command(name="rewards")
    async def rewards_cmd(self, ctx: commands.Context) -> None:
        await self._remember(ctx)
        rows = self.ops.recent_rewards(limit=6)
        if not rows:
            await ctx.reply("No reward scores yet — upload a Short and `!sync` after YouTube setup.")
            return
        lines = [f"**Recent scores**"]
        for r in rows:
            lines.append(f"• {r['video_label']}: **{r['verdict']}** ({r['score']})")
        await ctx.reply("\n".join(lines))

    @commands.command(name="status")
    async def status_cmd(self, ctx: commands.Context) -> None:
        await self._remember(ctx)
        s = self.ops.status()
        await ctx.reply(embed=status_embed(s, web_port=settings.web_port))

    @commands.command(name="chat")
    async def chat_cmd(self, ctx: commands.Context, *, message: str) -> None:
        await self._remember(ctx)
        async with ctx.typing():
            reply = await asyncio.to_thread(self.ops.chat, message)
        for part in _chunk(reply):
            await ctx.reply(part)

    @commands.command(name="draft")
    async def draft_cmd(self, ctx: commands.Context, *, topic: str) -> None:
        await self._remember(ctx)
        msg = await asyncio.to_thread(self.ops.create_draft, topic)
        await ctx.reply(msg)

    @commands.command(name="pending")
    async def pending_cmd(self, ctx: commands.Context) -> None:
        await self._remember(ctx)
        await ctx.reply(embed=pending_embed(self.ops.list_improvements(), self.ops.list_drafts()))

    @commands.command(name="yes")
    async def yes_cmd(self, ctx: commands.Context, imp_id: int) -> None:
        await self._remember(ctx)
        await ctx.reply(await asyncio.to_thread(self.ops.approve_improvement, imp_id))

    @commands.command(name="no")
    async def no_cmd(self, ctx: commands.Context, imp_id: int) -> None:
        await self._remember(ctx)
        await ctx.reply(await asyncio.to_thread(self.ops.reject_improvement, imp_id))

    @commands.command(name="draftyes")
    async def draft_yes(self, ctx: commands.Context, draft_id: int) -> None:
        await self._remember(ctx)
        await ctx.reply(await asyncio.to_thread(self.ops.approve_draft, draft_id))

    @commands.command(name="draftno")
    async def draft_no(self, ctx: commands.Context, draft_id: int, *, reason: str = "Rejected.") -> None:
        await self._remember(ctx)
        await ctx.reply(await asyncio.to_thread(self.ops.reject_draft, draft_id, reason))

    @commands.command(name="sync")
    async def sync_cmd(self, ctx: commands.Context) -> None:
        await self._remember(ctx)
        result = await asyncio.to_thread(self.ops.youtube_sync)
        await ctx.reply(result.get("message", "Done"))
        if result.get("improvements_created", 0) > 0:
            await notify_pending_summary(self.bot, self.ops)

    @commands.command(name="applybrand", aliases=["channelbrand"])
    async def apply_brand_cmd(self, ctx: commands.Context) -> None:
        """Apply channel name + description from youtube_copy.txt in YouTube Studio."""
        await self._remember(ctx)
        await ctx.reply("Opening browser to update channel name and description…")
        result = await asyncio.to_thread(self.ops.apply_channel_branding)
        msg = result.get("message", "Done")
        if result.get("name_updated"):
            msg += "\n✓ Name updated"
        if result.get("description_updated"):
            msg += "\n✓ Description updated"
        await ctx.reply(msg)

    @commands.command(name="produce")
    async def produce_cmd(self, ctx: commands.Context, *, payload: str) -> None:
        """Build image production pack: !produce 5 | 0:00 line\\n0:07 line"""
        await self._remember(ctx)
        if "|" not in payload:
            await ctx.reply("Usage: `!produce <draft_id> | <paste TurboScribe timestamps>`")
            return
        head, transcript = payload.split("|", 1)
        try:
            draft_id = int(head.strip().split()[-1])
        except ValueError:
            await ctx.reply("First part must include draft id, e.g. `!produce 5 | 0:00 ...`")
            return
        result = await asyncio.to_thread(self.ops.prepare_video_production, draft_id, transcript.strip())
        await ctx.reply(result.get("message", "Done"))

    @commands.command(name="notify")
    async def notify_cmd(self, ctx: commands.Context) -> None:
        """DM everyone on the notify list + anyone who has DMed the bot."""
        await self._remember(ctx)
        n = await dm_all(self.bot, build_morning_briefing())
        await ctx.reply(f"Sent briefing to {n} user(s).")

    @commands.command(name="dev")
    async def dev_cmd(self, ctx: commands.Context, *, payload: str) -> None:
        await self._remember(ctx)
        if "|" in payload:
            title, desc = payload.split("|", 1)
        else:
            title, desc = payload[:80], payload
        await ctx.reply(await asyncio.to_thread(self.ops.create_dev_task, title.strip(), desc.strip()))

    @commands.command(name="devpending")
    async def dev_pending(self, ctx: commands.Context) -> None:
        await self._remember(ctx)
        tasks = self.ops.list_dev_tasks()
        if not tasks:
            await ctx.reply("No pending dev tasks.")
            return
        lines = ["**Dev tasks**"]
        for t in tasks[:8]:
            lines.append(f"#{t['id']} {t['title']}")
        await ctx.reply("\n".join(lines))

    @commands.command(name="devyes")
    async def dev_yes(self, ctx: commands.Context, task_id: int) -> None:
        await self._remember(ctx)
        await ctx.reply(await asyncio.to_thread(self.ops.approve_dev_task, task_id))

    @commands.command(name="devno")
    async def dev_no(self, ctx: commands.Context, task_id: int) -> None:
        await self._remember(ctx)
        await ctx.reply(await asyncio.to_thread(self.ops.reject_dev_task, task_id))

    @commands.command(name="briefing")
    async def briefing_cmd(self, ctx: commands.Context) -> None:
        await self._remember(ctx)
        for part in _chunk(build_morning_briefing()):
            await ctx.reply(part)

    @app_commands.command(name="status", description="Shorts Bot system status")
    async def slash_status(self, interaction: discord.Interaction) -> None:
        s = self.ops.status()
        await interaction.response.send_message(embed=status_embed(s, web_port=settings.web_port))

    @app_commands.command(name="draft", description="Create a Short script draft")
    @app_commands.describe(topic="What the Short is about")
    async def slash_draft(self, interaction: discord.Interaction, topic: str) -> None:
        await interaction.response.defer(thinking=True)
        msg = await asyncio.to_thread(self.ops.create_draft, topic)
        await interaction.followup.send(msg)

    @app_commands.command(name="pending", description="List pending approvals")
    async def slash_pending(self, interaction: discord.Interaction) -> None:
        embed = pending_embed(self.ops.list_improvements(), self.ops.list_drafts())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="briefing", description="Morning checklist")
    async def slash_briefing(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(build_morning_briefing()[:1900])


def run_bot() -> None:
    if not settings.has_discord:
        raise SystemExit(
            "DISCORD_BOT_TOKEN missing in .env\n"
            "Discord Developer Portal → Bot → Reset Token → paste in .env"
        )
    bot = ShortsDiscordBot()
    bot.run(settings.discord_bot_token)
