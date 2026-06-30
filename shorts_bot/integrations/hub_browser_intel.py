"""Hub browser intel — read Discord web + course tools via saved login (read-only)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from shorts_bot.browser.session import browse_url
from shorts_bot.config import settings

INBOX = Path("data/research/course/inbox")


def intel_targets() -> list[tuple[str, str]]:
    """Named pages to scrape — owner logs in once on hub browser profile."""
    targets: list[tuple[str, str]] = []
    if settings.course_site_url:
        targets.append(("course-site", settings.course_site_url.strip()))
    if settings.course_bubble_tool_url:
        targets.append(("course-bubble-tool", settings.course_bubble_tool_url.strip()))
    guild = (settings.discord_guild_id or "").strip()
    channels = (settings.discord_channel_ids or "").replace(";", ",").split(",")
    for cid in channels:
        cid = cid.strip()
        if guild and cid:
            targets.append(
                (f"discord-{cid}", f"https://discord.com/channels/{guild}/{cid}")
            )
    return targets


def sync_hub_browser_inbox(*, screenshot: bool = False) -> Path:
    """Fetch allowlisted URLs using data/browser_profile cookies. Read-only."""
    targets = intel_targets()
    if not targets:
        raise RuntimeError(
            "No intel URLs configured — set COURSE_SITE_URL, COURSE_BUBBLE_TOOL_URL, "
            "and/or DISCORD_GUILD_ID + DISCORD_CHANNEL_IDS. See docs/FOR_OWNER_DISCORD_COURSE_INTEL.md"
        )

    INBOX.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = INBOX / f"hub-browser-sync-{stamp}.md"

    lines = [
        f"# Hub browser sync — {stamp}",
        "",
        "**Read-only.** Uses hub browser profile after owner login. Never clicks post/send.",
        "",
    ]

    for name, url in targets:
        result = browse_url(url, screenshot=screenshot, max_chars=12000)
        lines.append(f"## {name}")
        lines.append("")
        lines.append(f"- URL: {result.url}")
        lines.append(f"- Title: {result.title}")
        if result.logged_in_hint:
            lines.append(f"- Session: {result.logged_in_hint}")
        if result.screenshot_path:
            lines.append(f"- Screenshot: `{result.screenshot_path}`")
        lines.append("")
        lines.append(result.text or "(no text extracted)")
        lines.append("")

    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path
