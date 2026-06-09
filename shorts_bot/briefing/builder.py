from __future__ import annotations

from shorts_bot.config import settings
from shorts_bot.services.ops import BotOperations


def build_morning_briefing() -> str:
    ops = BotOperations()
    s = ops.status()
    yt = s["youtube"]
    lines = [
        "**Good morning — Shorts Bot briefing**",
        "",
        f"• Web UI: http://localhost:{settings.web_port}",
        f"• Chat: {'full (OpenAI)' if s['openai'] else 'offline — API key optional'}",
        f"• Discord: {'connected' if s['discord'] else 'needs DISCORD_BOT_TOKEN'}",
        "",
        "**Waiting for you (login/setup only):**",
    ]

    if not yt.get("credentials_configured"):
        lines.append("• Google API keys in `.env` — see docs/TOMORROW.md")
    elif not yt.get("token_saved"):
        lines.append("• Run once: `python3 -m shorts_bot.youtube.auth_cli`")
    else:
        lines.append("• YouTube Analytics: ready — tap Sync in web UI")

    if not s["openai"]:
        lines.append("• OpenAI API key optional — see docs/CHAT_TONIGHT.md")

    lines.extend(
        [
            "",
            "**Ready now (no login):**",
            f"• Pending improvements: {s['pending_improvements']} (Yes/No in web or Discord)",
            f"• Pending drafts: {s['pending_drafts']}",
            f"• Pending dev tasks: {s['pending_dev']}",
            "",
            "**Quick start:**",
            "`bash scripts/start.sh`  — web",
            "`python3 -m shorts_bot.discord_bot`  — Discord",
            "",
            "Reply `!help` on Discord for commands.",
        ]
    )
    return "\n".join(lines)
