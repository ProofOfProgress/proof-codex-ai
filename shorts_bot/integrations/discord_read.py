"""Read-only Discord ingest — fetch channel messages, never send."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from shorts_bot.config import settings

DISCORD_API = "https://discord.com/api/v10"
INBOX = Path("data/research/course/inbox")


@dataclass
class DiscordSetupStatus:
    configured: bool
    guild_id: str
    channel_ids: list[str]
    detail: str

    def __str__(self) -> str:
        channels = ", ".join(self.channel_ids) if self.channel_ids else "(none)"
        return (
            f"configured={self.configured} guild={self.guild_id or '-'} "
            f"channels=[{channels}] — {self.detail}"
        )


def _token() -> str:
    raw = (settings.discord_bot_token or "").strip()
    if not raw or "your" in raw.lower():
        raise RuntimeError(
            "DISCORD_BOT_TOKEN not set — see docs/FOR_OWNER_DISCORD_COURSE_INTEL.md"
        )
    return raw


def _headers() -> dict[str, str]:
    return {"Authorization": f"Bot {_token()}"}


def parse_channel_ids(raw: str | None = None) -> list[str]:
    text = (raw if raw is not None else settings.discord_channel_ids or "").strip()
    if not text:
        return []
    return [part.strip() for part in text.replace(";", ",").split(",") if part.strip()]


def discord_setup_status() -> DiscordSetupStatus:
    token = (settings.discord_bot_token or "").strip()
    guild = (settings.discord_guild_id or "").strip()
    channels = parse_channel_ids()
    if not token or "your" in token.lower():
        return DiscordSetupStatus(False, guild, channels, "missing bot token")
    if not channels:
        return DiscordSetupStatus(False, guild, channels, "missing DISCORD_CHANNEL_IDS allowlist")
    return DiscordSetupStatus(True, guild, channels, "ready for read-only sync")


def _get_json(client: httpx.Client, path: str) -> Any:
    resp = client.get(f"{DISCORD_API}{path}", headers=_headers(), timeout=30.0)
    if resp.status_code >= 400:
        raise RuntimeError(f"Discord API {path} → {resp.status_code}: {resp.text[:300]}")
    return resp.json()


def fetch_channel_messages(
    channel_id: str,
    *,
    limit: int = 50,
    before: str | None = None,
) -> list[dict[str, Any]]:
    """GET messages only — bot must have Read Message History; no send endpoints."""
    limit = max(1, min(int(limit), 100))
    params: dict[str, str | int] = {"limit": limit}
    if before:
        params["before"] = before
    with httpx.Client() as client:
        resp = client.get(
            f"{DISCORD_API}/channels/{channel_id}/messages",
            headers=_headers(),
            params=params,
            timeout=30.0,
        )
        if resp.status_code >= 400:
            raise RuntimeError(
                f"Discord channel {channel_id} → {resp.status_code}: {resp.text[:300]}"
            )
        data = resp.json()
        if not isinstance(data, list):
            raise RuntimeError(f"Unexpected Discord response for channel {channel_id}")
        return data


def _author_label(msg: dict[str, Any]) -> str:
    author = msg.get("author") or {}
    name = author.get("global_name") or author.get("username") or "unknown"
    return str(name)


def _message_line(msg: dict[str, Any]) -> str:
    ts = msg.get("timestamp") or ""
    content = (msg.get("content") or "").strip()
    embeds = msg.get("embeds") or []
    embed_text = ""
    if embeds and isinstance(embeds, list):
        parts = []
        for emb in embeds[:3]:
            if not isinstance(emb, dict):
                continue
            title = (emb.get("title") or "").strip()
            desc = (emb.get("description") or "").strip()
            if title:
                parts.append(title)
            if desc:
                parts.append(desc)
        embed_text = " | ".join(parts)
    body = content or embed_text or "(no text — attachment/embed only)"
    attachments = msg.get("attachments") or []
    if attachments:
        urls = [a.get("url", "") for a in attachments if isinstance(a, dict) and a.get("url")]
        if urls:
            body += "\n  attachments: " + ", ".join(urls[:5])
    return f"- **{ts}** `{_author_label(msg)}`: {body}"


def render_channel_markdown(channel_id: str, messages: list[dict[str, Any]]) -> str:
    lines = [f"## Channel `{channel_id}`", ""]
    if not messages:
        lines.append("(no messages fetched)")
        return "\n".join(lines)
    # Discord returns newest-first; store oldest-first for reading
    for msg in reversed(messages):
        lines.append(_message_line(msg))
    return "\n".join(lines)


def sync_discord_inbox(
    *,
    limit_per_channel: int = 50,
    channel_ids: list[str] | None = None,
    out_dir: Path | None = None,
) -> Path:
    """Fetch allowlisted channels and write markdown to course inbox. Read-only."""
    st = discord_setup_status()
    if not st.configured:
        raise RuntimeError(str(st))

    ids = channel_ids or st.channel_ids
    out = out_dir or INBOX
    out.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = out / f"discord-sync-{stamp}.md"

    sections = [
        f"# Discord sync — {stamp}",
        "",
        "**Read-only ingest.** Bot never sends messages.",
        "",
        f"Guild: `{st.guild_id or 'n/a'}`",
        "",
    ]

    for cid in ids:
        messages = fetch_channel_messages(cid, limit=limit_per_channel)
        sections.append(render_channel_markdown(cid, messages))
        sections.append("")

    path.write_text("\n".join(sections).rstrip() + "\n", encoding="utf-8")

    state_path = out / "discord_sync_state.json"
    state = {
        "last_sync_utc": datetime.now(timezone.utc).isoformat(),
        "channels": ids,
        "limit_per_channel": limit_per_channel,
        "output": str(path),
    }
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    return path
