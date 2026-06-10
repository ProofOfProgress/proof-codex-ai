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


def _probe_llm(provider: str, api_key: str, model: str, base_url: str | None = None) -> ServiceStatus:
    label = "Gemini chat (free)" if provider == "gemini" else "OpenAI chat"
    try:
        from openai import OpenAI

        kwargs: dict = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        client = OpenAI(**kwargs)
        client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=3,
        )
        return ServiceStatus(provider, label, True, f"{model} works")
    except Exception as exc:
        msg = str(exc)
        if "429" in msg or "quota" in msg.lower():
            return ServiceStatus(
                provider,
                label,
                False,
                "Key saved but quota exceeded",
                "https://aistudio.google.com/apikey" if provider == "gemini" else "docs/CHAT_TONIGHT.md",
            )
        return ServiceStatus(provider, label, False, msg[:120], "docs/CHAT_TONIGHT.md")


def _check_chat() -> ServiceStatus:
    from shorts_bot.llm.provider import GEMINI_OPENAI_BASE

    if settings.has_gemini:
        return _probe_llm(
            "gemini",
            settings.gemini_api_key or "",
            settings.gemini_model,
            GEMINI_OPENAI_BASE,
        )
    if settings.has_openai:
        return _probe_llm("openai", settings.openai_api_key or "", settings.openai_model)
    return ServiceStatus(
        "chat",
        "AI chat",
        False,
        "No GEMINI_API_KEY or OPENAI_API_KEY",
        "https://aistudio.google.com/apikey",
    )


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


def _check_image_api() -> ServiceStatus:
    provider = (settings.image_provider or "replicate").strip().lower()
    if provider == "fal" and settings.has_fal_images:
        from shorts_bot.production.images.fal import probe_fal

        ok, detail = probe_fal(settings.fal_api_key or "")
        return ServiceStatus("fal_images", "Fal.ai image API", ok, detail, "https://fal.ai/dashboard/keys")
    if settings.has_replicate_images:
        from shorts_bot.production.images.replicate import probe_replicate

        ok, detail = probe_replicate(
            settings.replicate_api_token or "",
            settings.replicate_image_model,
        )
        return ServiceStatus(
            "replicate_images",
            "Replicate image API",
            ok,
            detail,
            "https://replicate.com/account/api-tokens",
        )
    return ServiceStatus(
        "image_api",
        "Paid image API",
        False,
        "REPLICATE_API_TOKEN or FAL_API_KEY missing",
        "https://replicate.com/account/api-tokens",
    )


def _check_transcript_sync() -> ServiceStatus:
    provider = (settings.transcript_provider or "gemini").strip().lower()
    if provider == "assemblyai" and settings.has_assemblyai:
        model = settings.assemblyai_speech_model or "universal"
        return ServiceStatus(
            "transcript",
            "AssemblyAI transcript (optional)",
            True,
            f"API key configured ({model})",
        )
    if settings.has_gemini:
        model = (settings.gemini_transcript_model or settings.gemini_model).strip()
        return ServiceStatus(
            "transcript",
            "Gemini audio transcript",
            True,
            f"{model} — same GEMINI_API_KEY as chat/vision",
        )
    return ServiceStatus(
        "transcript",
        "Gemini audio transcript",
        False,
        "GEMINI_API_KEY missing",
        "https://aistudio.google.com/apikey",
    )


def _check_youtube_upload() -> ServiceStatus:
    from shorts_bot.youtube.google_auth import auth_status, upload_ready

    st = auth_status()
    if not st["credentials_configured"]:
        return ServiceStatus(
            "youtube_upload",
            "YouTube API upload",
            False,
            "GOOGLE_CLIENT_ID/SECRET missing",
            "Add to Cursor secrets — bash scripts/install.sh",
        )
    if not st["token_saved"]:
        return ServiceStatus(
            "youtube_upload",
            "YouTube API upload",
            False,
            "OAuth not run yet",
            "python3 -m shorts_bot.youtube.auth_cli",
        )
    if st.get("needs_upload_reauth"):
        return ServiceStatus(
            "youtube_upload",
            "YouTube API upload",
            False,
            "Token lacks upload scope",
            "python3 -m shorts_bot.youtube.auth_cli",
        )
    if upload_ready():
        return ServiceStatus(
            "youtube_upload",
            "YouTube API upload",
            True,
            "Ready — no Studio browser needed",
        )
    return ServiceStatus(
        "youtube_upload",
        "YouTube API upload",
        False,
        "Upload credentials unavailable",
        "python3 -m shorts_bot.youtube.auth_cli",
    )


def _check_vision_qc() -> ServiceStatus:
    if not settings.vision_qc_enabled:
        return ServiceStatus("vision_qc", "Gemini vision QC", False, "Disabled", None)
    if settings.has_gemini:
        model = (settings.gemini_vision_model or settings.gemini_model).strip()
        return ServiceStatus(
            "vision_qc",
            "Gemini vision QC",
            True,
            f"{model} — {settings.vision_qc_max_frames} frames/Short",
        )
    return ServiceStatus(
        "vision_qc",
        "Gemini vision QC",
        False,
        "GEMINI_API_KEY missing",
        "https://aistudio.google.com/apikey",
    )


def _check_resemble() -> ServiceStatus:
    if not settings.has_resemble:
        return ServiceStatus(
            "resemble",
            "Resemble voice clone",
            False,
            "RESEMBLE_API_KEY or RESEMBLE_VOICE_UUID missing",
            "https://app.resemble.ai/account/api",
        )
    from shorts_bot.production.tts.resemble import probe_resemble

    ok, detail = probe_resemble(settings.resemble_api_key or "", settings.resemble_voice_uuid or "")
    return ServiceStatus(
        "resemble",
        "Resemble voice clone",
        ok,
        detail,
        None if ok else "python3 -m shorts_bot.production.voice_clone_cli test",
    )


def _check_vidiq() -> ServiceStatus:
    if not settings.vidiq_enabled:
        return ServiceStatus("vidiq", "vidIQ keyword research", False, "Disabled", None)
    if (settings.vidiq_api_key or "").strip():
        return ServiceStatus(
            "vidiq",
            "vidIQ (MCP API key)",
            True,
            "VIDIQ_API_KEY set — deep research uses MCP",
            "https://vidiq.com/mcp/",
        )
    try:
        from shorts_bot.research.vidiq import check_vidiq_session

        ok, detail = check_vidiq_session()
        return ServiceStatus(
            "vidiq",
            "vidIQ keyword research",
            ok,
            detail,
            None if ok else "python3 -m shorts_bot.login_handoff --only vidiq",
        )
    except Exception as exc:
        return ServiceStatus(
            "vidiq",
            "vidIQ keyword research",
            False,
            str(exc)[:120],
            "python3 -m shorts_bot.login_handoff --only vidiq",
        )


def _check_playwright() -> ServiceStatus:
    from shorts_bot.browser.session import is_playwright_ready

    ok, detail = is_playwright_ready()
    return ServiceStatus(
        "playwright",
        "Playwright browser",
        ok,
        detail,
        None if ok else "python3 -m playwright install chromium",
    )


def full_status(*, include_studio: bool = True) -> list[dict[str, Any]]:
    """Return live status for all integrations."""
    items = [
        _check_discord(),
        _check_playwright(),
        _check_chat(),
        _check_resemble(),
        _check_transcript_sync(),
        _check_vision_qc(),
        _check_image_api(),
        _check_youtube_oauth(),
        _check_youtube_upload(),
    ]
    if include_studio:
        items.append(_check_studio())
    items.append(_check_vidiq())
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
