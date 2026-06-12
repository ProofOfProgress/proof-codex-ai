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


def _strip_mention(message: discord.Message, bot_user: discord.ClientUser | None) -> str:
    text = (message.content or "").strip()
    if not bot_user:
        return text
    text = text.replace(f"<@{bot_user.id}>", "").replace(f"<@!{bot_user.id}>", "").strip()
    return text


def _is_owner(user_id: int) -> bool:
    owner = (settings.discord_owner_id or "").strip()
    return bool(owner) and str(user_id) == owner


class ShortsDiscordBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.dm_messages = True
        intents.guilds = True
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
        cog.auto_analytics_sync.start()
        cog.publish_queue_check.start()
        if settings.auto_daily_enabled:
            cog.auto_daily_short.start()
        try:
            synced = await self.tree.sync()
            log.info("Synced %s slash command(s)", len(synced))
        except Exception as exc:  # noqa: BLE001
            log.warning("Slash command sync failed: %s", exc)

    async def on_ready(self) -> None:
        log.info("Discord bot ready as %s (v%s)", self.user, __version__)
        if settings.discord_set_avatar_on_start:
            try:
                from shorts_bot.discord_bot.avatar import set_bot_avatar

                await set_bot_avatar(self)
            except Exception as exc:  # noqa: BLE001
                log.warning("Discord avatar update skipped: %s", exc)
        if settings.discord_send_briefing_on_start and not self._briefing_sent:
            self._briefing_sent = True
            await self._send_briefing()
            await notify_pending_summary(self, self.ops)

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        if isinstance(message.channel, discord.DMChannel):
            remember_dm_user(message.author.id)

        content = (message.content or "").strip()
        prefix = settings.discord_command_prefix
        is_dm = isinstance(message.channel, discord.DMChannel)
        mentioned = self.user is not None and self.user in message.mentions
        owner_chat = _is_owner(message.author.id) and not is_dm

        # Free-form chat: DMs, @mention, or owner messages in servers (no ! prefix)
        if content and not content.startswith(prefix):
            if is_dm or mentioned or owner_chat:
                clean = _strip_mention(message, self.user)
                if clean:
                    await self._reply_chat(message, clean)
                    return

        try:
            await self.process_commands(message)
        except Exception as exc:  # noqa: BLE001
            log.exception("Command failed")
            try:
                await message.channel.send(f"Command error: {exc}"[:1900])
            except Exception:
                pass

    async def _reply_chat(self, message: discord.Message, text: str) -> None:
        try:
            async with message.channel.typing():
                reply = await asyncio.to_thread(self.ops.chat, text)
            for part in _chunk(reply):
                await message.channel.send(part)
        except Exception as exc:  # noqa: BLE001
            log.exception("Discord chat failed")
            await message.channel.send(
                f"Something broke — try `!help` or `!ping`. Error: `{exc}`"[:1900]
            )

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
        self.auto_analytics_sync.cancel()
        self.publish_queue_check.cancel()
        self.auto_daily_short.cancel()

    @tasks.loop(hours=1)
    async def publish_queue_check(self) -> None:
        if settings.auto_publish_hours <= 0:
            return
        await self.bot.wait_until_ready()
        from shorts_bot.automation.coordinator import process_publish_queue
        from shorts_bot.web.deps import get_memory

        n = await asyncio.to_thread(process_publish_queue, get_memory())
        if n:
            await dm_all(self.bot, f"Auto-published {n} Short(s) to public.")

    @publish_queue_check.before_loop
    async def before_publish(self) -> None:
        await self.bot.wait_until_ready()

    @tasks.loop(hours=max(1, settings.auto_analytics_sync_interval_hours))
    async def auto_analytics_sync(self) -> None:
        if not settings.auto_analytics_sync:
            return
        await self.bot.wait_until_ready()
        result = await asyncio.to_thread(self.ops.youtube_sync)
        if result.get("ok") and result.get("improvements_created", 0) > 0:
            await notify_pending_summary(self.bot, self.ops)

    @auto_analytics_sync.before_loop
    async def before_auto_sync(self) -> None:
        await self.bot.wait_until_ready()

    @tasks.loop(time=datetime.time(hour=settings.auto_daily_hour, minute=settings.auto_daily_minute))
    async def auto_daily_short(self) -> None:
        await self.bot.wait_until_ready()
        msg = await asyncio.to_thread(self.ops.run_daily_short)
        await dm_all(self.bot, f"**Auto daily Short**\n{msg[:1800]}")

    @auto_daily_short.before_loop
    async def before_auto_daily(self) -> None:
        await self.bot.wait_until_ready()

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

    async def _reply_ops(self, ctx: commands.Context, text: str) -> None:
        for part in _chunk(text):
            await ctx.reply(part)

    @commands.command(name="help")
    async def help_cmd(self, ctx: commands.Context) -> None:
        await self._remember(ctx)
        await ctx.reply(
            "**Don't Blink Bot**\n\n"
            "**DMs:** type normally (no `!`).\n"
            "**Servers:** `!command` or `@Bot your message` (owner can type without @).\n\n"
            "**Pipeline:**\n"
            "`!daily` · `!research <topic>` · `!deepresearch <topic>`\n"
            "`!finish <id>` · `!makevideo <id>` · `!applybrand` · `!live`\n\n"
            "**Browser (Playwright — saved login profile):**\n"
            "`!browse <url>` · `!browser open vidiq` · `!browser login youtube`\n\n"
            "**Memory:** `!remember <rule>` · `!memory` · `!forget <id>`\n"
            "**Approvals:** `!pending` · `!yes` / `!no` · `!draftyes` / `!draftno`\n"
            "`!status` · `!sync` · `!briefing` · `!ping` · `!myid`\n"
            "Slash: `/daily` `/status` `/draft` `/pending` `/briefing`"
        )

    @commands.command(name="remember")
    async def remember_cmd(self, ctx: commands.Context, *, text: str) -> None:
        """Save an operating rule or fact for future sessions."""
        await self._remember(ctx)
        msg = await asyncio.to_thread(self.ops.remember_agent_memory, text.strip())
        await ctx.reply(msg)

    @commands.command(name="memory", aliases=["memories", "rules"])
    async def memory_cmd(self, ctx: commands.Context) -> None:
        await self._remember(ctx)
        msg = await asyncio.to_thread(self.ops.list_agent_memory)
        await self._reply_ops(ctx, msg)

    @commands.command(name="forget")
    async def forget_cmd(self, ctx: commands.Context, memory_id: int) -> None:
        await self._remember(ctx)
        msg = await asyncio.to_thread(self.ops.forget_agent_memory, memory_id)
        await ctx.reply(msg)

    @commands.command(name="ping")
    async def ping_cmd(self, ctx: commands.Context) -> None:
        await self._remember(ctx)
        lat = round(self.bot.latency * 1000)
        await ctx.reply(f"Pong — {lat}ms · v{__version__} · I'm online.")

    @commands.command(name="myid")
    async def myid_cmd(self, ctx: commands.Context) -> None:
        await self._remember(ctx)
        uid = ctx.author.id
        await ctx.reply(
            f"Your user ID: `{uid}`\n"
            f"Set in `.env`: `DISCORD_OWNER_ID={uid}` for owner chat in servers."
        )

    @commands.command(name="live", aliases=["loginstatus", "health"])
    async def live_cmd(self, ctx: commands.Context) -> None:
        await self._remember(ctx)
        async with ctx.typing():
            text = await asyncio.to_thread(self.ops.login_status_text)
        await self._reply_ops(ctx, text)

    @commands.command(name="daily")
    async def daily_cmd(self, ctx: commands.Context, *, topic: str | None = None) -> None:
        """Full autopilot Short: !daily or !daily the minute before a hard conversation"""
        await self._remember(ctx)
        await ctx.reply("Starting daily pipeline (research → draft → render → upload)…")
        async with ctx.typing():
            msg = await asyncio.to_thread(self.ops.run_daily_short, topic)
        await self._reply_ops(ctx, msg)

    @commands.command(name="browse")
    async def browse_cmd(self, ctx: commands.Context, *, url: str) -> None:
        await self._remember(ctx)
        await ctx.reply(f"Browsing (headless): {url[:120]}…")
        async with ctx.typing():
            msg = await asyncio.to_thread(self.ops.browse_web, url)
        await self._reply_ops(ctx, msg)

    @commands.command(name="browser")
    async def browser_cmd(self, ctx: commands.Context, action: str | None = None, *, target: str | None = None) -> None:
        await self._remember(ctx)
        act = (action or "").lower()
        if act in {"status", ""} and not target:
            msg = await asyncio.to_thread(self.ops.browser_status_text)
            await ctx.reply(msg)
            return
        if act == "open" and target:
            msg = await asyncio.to_thread(self.ops.open_browser, target)
            await ctx.reply(msg)
            return
        if act == "login" and target:
            msg = await asyncio.to_thread(self.ops.open_browser, target)
            await ctx.reply(msg)
            return
        if act == "browse" and target:
            async with ctx.typing():
                msg = await asyncio.to_thread(self.ops.browse_web, target)
            await self._reply_ops(ctx, msg)
            return
        await ctx.reply("Usage: `!browser status` · `!browser open vidiq` · `!browser login youtube` · `!browse <url>`")

    @commands.command(name="research")
    async def research_cmd(self, ctx: commands.Context, *, topic: str) -> None:
        await self._remember(ctx)
        await ctx.reply(f"Deep researching (web + vidIQ + competitors): {topic[:80]}…")
        async with ctx.typing():
            msg = await asyncio.to_thread(self.ops.run_research, topic)
        await self._reply_ops(ctx, msg)

    @commands.command(name="deepresearch", aliases=["deep_research"])
    async def deep_research_cmd(self, ctx: commands.Context, *, topic: str) -> None:
        await self._remember(ctx)
        await ctx.reply(f"Force-refresh deep research: {topic[:80]}…")
        async with ctx.typing():
            msg = await asyncio.to_thread(self.ops.run_research, topic, force_refresh=True)
        await self._reply_ops(ctx, msg)

    @commands.command(name="finish", aliases=["finishvideo"])
    async def finish_cmd(self, ctx: commands.Context, draft_id: int) -> None:
        await self._remember(ctx)
        await ctx.reply(f"Finishing draft #{draft_id}…")
        async with ctx.typing():
            result = await asyncio.to_thread(self.ops.finish_video, draft_id)
        await self._reply_ops(ctx, result.get("message", "Done"))

    @commands.command(name="brandassets", aliases=["generateassets"])
    async def brand_assets_cmd(self, ctx: commands.Context) -> None:
        await self._remember(ctx)
        msg = await asyncio.to_thread(self.ops.generate_brand_assets)
        await ctx.reply(msg)

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
        lines = ["**Recent scores**"]
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
        await self._reply_chat(ctx, message)

    async def _reply_chat(self, ctx: commands.Context, text: str) -> None:
        async with ctx.typing():
            reply = await asyncio.to_thread(self.ops.chat, text)
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
        if result.get("improvements_created", 0) > 0 or result.get("comments_queued_human", 0) > 0:
            await notify_pending_summary(self.bot, self.ops)

    @commands.command(name="comments")
    async def comments_cmd(self, ctx: commands.Context, action: str | None = None) -> None:
        """Auto-reply light comments; use `!comments pending` for serious queue."""
        await self._remember(ctx)
        if action and action.lower() == "pending":
            msg = await asyncio.to_thread(self.ops.format_comments_pending)
        else:
            result = await asyncio.to_thread(self.ops.run_comment_replies)
            msg = result.get("message", "Done")
            if result.get("queued_human", 0) > 0:
                await notify_pending_summary(self.bot, self.ops)
        for part in _chunk(msg):
            await ctx.reply(part)

    @commands.command(name="applybrand", aliases=["channelbrand", "brand"])
    async def apply_brand_cmd(self, ctx: commands.Context) -> None:
        """Apply name + description + banner via YouTube API (no browser)."""
        await self._remember(ctx)
        await ctx.reply("Updating channel via YouTube API…")
        result = await asyncio.to_thread(self.ops.apply_channel_branding)
        msg = result.get("message", "Done")
        await self._reply_ops(ctx, msg)

    @commands.command(name="makevideo")
    async def make_video_cmd(self, ctx: commands.Context, draft_id: int) -> None:
        await self._remember(ctx)
        result = await asyncio.to_thread(self.ops.auto_make_video, draft_id)
        await ctx.reply(result.get("message", "Done"))

    @commands.command(name="voice")
    async def voice_cmd(self, ctx: commands.Context, draft_id: int) -> None:
        await self._remember(ctx)
        result = await asyncio.to_thread(self.ops.generate_voiceover, draft_id)
        await ctx.reply(result.get("message", "Done"))

    @commands.command(name="produce")
    async def produce_cmd(self, ctx: commands.Context, *, payload: str) -> None:
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

    @app_commands.command(name="daily", description="Run full daily Short pipeline")
    @app_commands.describe(topic="Optional topic override")
    async def slash_daily(self, interaction: discord.Interaction, topic: str | None = None) -> None:
        await interaction.response.defer(thinking=True)
        msg = await asyncio.to_thread(self.ops.run_daily_short, topic)
        for part in _chunk(msg):
            await interaction.followup.send(part)

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
    logging.basicConfig(level=logging.INFO)
    if not settings.has_discord:
        raise SystemExit(
            "DISCORD_BOT_TOKEN missing in .env\n"
            "Discord Developer Portal → Bot → Reset Token → paste in .env"
        )
    bot = ShortsDiscordBot()
    bot.run(settings.discord_bot_token, log_handler=None)
