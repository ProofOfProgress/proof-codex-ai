from __future__ import annotations

import logging

import discord

from shorts_bot.discord_bot.prefs import briefing_user_ids

log = logging.getLogger(__name__)


async def dm_all(bot: discord.Client, text: str, *, chunk: int = 1900) -> int:
    """DM everyone in notify list + remembered DM users. Returns success count."""
    sent = 0
    for user_id in briefing_user_ids():
        if not user_id.isdigit():
            continue
        try:
            user = await bot.fetch_user(int(user_id))
            while text:
                part, text = text[:chunk], text[chunk:]
                await user.send(part)
            sent += 1
        except Exception as exc:  # noqa: BLE001
            log.warning("Notify failed for %s: %s", user_id, exc)
    return sent


async def notify_pending_summary(bot: discord.Client, ops) -> None:
    s = ops.status()
    if s["pending_improvements"] + s["pending_drafts"] + s["pending_dev"] == 0:
        return
    msg = (
        "**Shorts Bot — needs your tap**\n"
        f"• Improvements: {s['pending_improvements']} → `!pending` then `!yes <id>`\n"
        f"• Drafts: {s['pending_drafts']}\n"
        f"• Dev tasks: {s['pending_dev']}\n"
        f"Web: http://localhost:8080"
    )
    await dm_all(bot, msg)
