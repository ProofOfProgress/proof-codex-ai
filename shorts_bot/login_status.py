"""Live integration status — keys present vs actually working."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any

from shorts_bot.config import settings
from shorts_bot.youtube.google_auth import auth_status


@dataclass
class ServiceStatus:
    id: str
    label: str
    ready: bool
    detail: str
    action: str | None = None


def _check_openai() -> ServiceStatus:
    if not settings.has_openai:
        return ServiceStatus(
            "openai",
            "OpenAI chat",
            False,
            "No API key",
            "docs/CHAT_TONIGHT.md or add GEMINI_API_KEY (free)",
        )
    try:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)
        client.chat.completions.create(
            model=settings.openai_model,
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=3,
        )
        return ServiceStatus("openai", "OpenAI chat", True, "API key works")
    except Exception as exc:
        msg = str(exc)
        if "429" in msg or "quota" in msg.lower():
            return ServiceStatus(
                "openai",
                "OpenAI chat",
                False,
                "Key saved but quota exceeded — add billing or use free Gemini",
                "https://aistudio.google.com/apikey",
            )
        return ServiceStatus("openai", "OpenAI chat", False, msg[:120], "docs/CHAT_TONIGHT.md")


def _check_youtube_oauth() -> ServiceStatus:
    yt = auth_status()
    if not yt.get("ready"):
        return ServiceStatus(
            "youtube_oauth",
            "YouTube Analytics API",
            False,
            "OAuth token missing",
            "python3 -m shorts_bot.youtube.auth_cli",
        )
    try:
        from shorts_bot.web.deps import get_analytics_sync

        result = get_analytics_sync().run(max_videos=1)
        if result.ok:
            return ServiceStatus(
                "youtube_oauth",
                "YouTube Analytics API",
                True,
                result.message,
            )
        return ServiceStatus(
            "youtube_oauth",
            "YouTube Analytics API",
            False,
            result.message,
            "python3 -m shorts_bot.youtube.auth_cli",
        )
    except Exception as exc:
        return ServiceStatus(
            "youtube_oauth",
            "YouTube Analytics API",
            False,
            str(exc)[:120],
            "python3 -m shorts_bot.youtube.auth_cli",
        )


def _check_studio() -> ServiceStatus:
    try:
        from shorts_bot.youtube.studio import check_studio

        live = check_studio(settings.browser_profile_dir, headless=True)
        if live.logged_in and live.in_studio:
            name = live.channel_name or settings.youtube_channel_name
            return ServiceStatus(
                "youtube_studio",
                "YouTube Studio (browser)",
                True,
                f"Logged in — {name}",
            )
        return ServiceStatus(
            "youtube_studio",
            "YouTube Studio (browser)",
            False,
            live.message or "Not signed in",
            "python3 -m shorts_bot.youtube.keep_browser_open",
        )
    except Exception as exc:
        return ServiceStatus(
            "youtube_studio",
            "YouTube Studio (browser)",
            False,
            str(exc)[:120],
            "python3 -m shorts_bot.youtube.keep_browser_open",
        )


def _check_discord() -> ServiceStatus:
    if not settings.has_discord:
        return ServiceStatus(
            "discord",
            "Discord bot",
            False,
            "No bot token",
            "docs/MORNING.md",
        )
    owner = settings.discord_owner_id or "(auto from DM)"
    return ServiceStatus("discord", "Discord bot", True, f"Token set — owner {owner}")


def _check_browser_site(
    id_: str,
    label: str,
    url: str,
    *,
    logged_in_hint: str,
    fallback_note: str,
) -> ServiceStatus:
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(settings.browser_profile_dir),
                headless=True,
                viewport={"width": 1280, "height": 900},
            )
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=90000)
            body = (page.inner_text("body") or "").lower()
            context.close()
        if logged_in_hint.lower() in body or "sign out" in body or "log out" in body:
            return ServiceStatus(id_, label, True, "Browser session saved")
        if "sign in" in body or "log in" in body or "sign up" in body:
            return ServiceStatus(
                id_,
                label,
                False,
                "Not signed in",
                f"python3 -m shorts_bot.login_handoff --only {id_}",
            )
        return ServiceStatus(id_, label, True, "Page loaded (session likely active)")
    except Exception as exc:
        return ServiceStatus(
            id_,
            label,
            False,
            fallback_note,
            f"python3 -m shorts_bot.login_handoff --only {id_} ({exc})",
        )


def full_status(*, include_studio: bool = True) -> list[dict[str, Any]]:
    """Return live status for all integrations."""
    items = [
        _check_discord(),
        _check_openai(),
        _check_youtube_oauth(),
    ]
    if include_studio:
        items.append(_check_studio())
    items.extend(
        [
            _check_browser_site(
                "turboscribe",
                "TurboScribe (optional)",
                "https://turboscribe.ai/dashboard",
                logged_in_hint="transcription",
                fallback_note="Optional — use make video to skip TurboScribe",
            ),
            _check_browser_site(
                "capcut",
                "CapCut (your edit step)",
                "https://www.capcut.com/my-edit",
                logged_in_hint="create",
                fallback_note="Import production pack images + your voiceover",
            ),
        ]
    )
    return [asdict(s) for s in items]


def print_report() -> int:
    from rich.console import Console
    from rich.table import Table

    console = Console()
    table = Table(title="Soft Continuity — live login status")
    table.add_column("Service")
    table.add_column("Ready")
    table.add_column("Detail")
    table.add_column("If not done")

    not_ready = 0
    for row in full_status():
        ready = "✓" if row["ready"] else "—"
        if not row["ready"]:
            not_ready += 1
        table.add_row(row["label"], ready, row["detail"], row.get("action") or "")
    console.print(table)
    console.print(f"\n[bold]{len(full_status()) - not_ready}[/bold] ready, [yellow]{not_ready}[/yellow] need attention")
    return 0 if not_ready <= 2 else 1  # turboscribe+capcut are optional manual


if __name__ == "__main__":
    raise SystemExit(print_report())
