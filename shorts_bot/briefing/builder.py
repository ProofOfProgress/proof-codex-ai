from __future__ import annotations

from shorts_bot.config import settings
from shorts_bot.services.ops import BotOperations


def build_morning_briefing() -> str:
    ops = BotOperations()
    s = ops.status()
    yt = s["youtube"]
    lines = [
        "**Good morning — PERIPHERAL**",
        "_PERIPHERAL — you're already in it. 🔊 hard ending._",
        "",
        f"• Web UI: http://localhost:{settings.web_port}",
        f"• Chat: {'full (OpenAI)' if s['openai'] else 'offline — API key optional'}",
        f"• Discord: {'connected' if s['discord'] else 'needs DISCORD_BOT_TOKEN'}",
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
            f"• Daily Short at {settings.auto_daily_hour:02d}:{settings.auto_daily_minute:02d} UTC" if settings.auto_daily_enabled else "• Daily Short: manual `!daily`",
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
            "`bash scripts/start.sh`  — web",
            "`python3 -m shorts_bot.discord_bot`  — Discord",
            "",
            "Discord: type normally in DM (no ! prefix) or `!help` in servers.",
        ]
    )
    return "\n".join(lines)
