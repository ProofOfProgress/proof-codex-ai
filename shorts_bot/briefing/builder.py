from __future__ import annotations

from shorts_bot.config import settings
from shorts_bot.services.ops import BotOperations


def build_morning_briefing() -> str:
    ops = BotOperations()
    s = ops.status()
    yt = s["youtube"]
    lines = [
        "**Good morning — Peripheral**",
        "_Peripheral — watch the whole thing. don't blink. 🔊 jumpscare on finale beats._",
        "",
        f"• Web UI: http://localhost:{settings.web_port} (chat + approvals)",
        f"• Chat: {'full' if s['openai'] else 'offline — add GEMINI_API_KEY or OPENAI_API_KEY'}",
        "",
        "**You only (login / payments):**",
    ]

    if not yt.get("credentials_configured"):
        lines.append("• Google API keys in `.env` — see docs/TOMORROW.md")
    elif not yt.get("token_saved"):
        lines.append(
            "• YouTube OAuth once: `python3 -m shorts_bot.youtube.auth_cli` — see docs/TOMORROW.md"
        )
    else:
        lines.append("• YouTube OAuth done — analytics sync runs automatically")

    if not s["openai"]:
        lines.append("• OpenAI API key optional — see docs/CHAT_TONIGHT.md")

    lines.extend(
        [
            "",
            "**Automated (no tap needed):**",
            f"• Analytics sync every {settings.auto_analytics_sync_interval_hours}h (safe improvements auto-Yes)",
            f"• Daily Short at {settings.auto_daily_hour:02d}:{settings.auto_daily_minute:02d} UTC" if settings.auto_daily_enabled else "• Daily Short: type `daily` in web chat",
            f"• Unlisted → public after {settings.auto_publish_hours}h" if settings.auto_publish_hours > 0 else "• Upload visibility: as configured",
            "• Light YouTube comments auto-reply; serious ones queued for you",
            "",
            "**Still needs you (if any):**",
            f"• Risky improvements: {s['pending_improvements']}",
            f"• Pending drafts: {s['pending_drafts']}",
            f"• Login/payment dev tasks: {s['pending_dev']}",
            f"• Serious comments: {s.get('pending_comments', 0)} (`comments pending`)",
            "",
            "**Quick start:**",
            "`bash scripts/start.sh`  — web UI",
            "`GET /api/briefing`  — this checklist as JSON/text",
            "",
            "**Slack (remote):**",
            "• `@cursor agent …` — start Cloud Agent from phone (docs/SLACK_CURSOR_SETUP.md)",
            _slack_briefing_line(),
        ]
    )
    return "\n".join(lines)


def _slack_briefing_line() -> str:
    from shorts_bot.integrations.slack import has_slack_bot, has_slack_webhook

    ch = settings.slack_channel_name
    if has_slack_bot():
        return f"• {settings.slack_bot_display_name} bot → #{ch} (live)"
    if has_slack_webhook():
        return f"• Pipeline alerts → #{ch} (webhook live)"
    return "• Slack bot: docs/FOR_OWNER_SLACK_BOT.md (SLACK_BOT_TOKEN + SLACK_CHANNEL_ID)"
