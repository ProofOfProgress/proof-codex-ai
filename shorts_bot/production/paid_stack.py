"""Enforce paid production stack — Resemble voice + Gemini transcript/vision."""

from __future__ import annotations

from shorts_bot.config import settings

_TIMESTAMP_SOURCES = frozenset({"turboscribe", "cache", "assemblyai", "gemini"})
_SCRIPT_FALLBACK_SOURCES = frozenset({"script_duration", "script_estimate"})


def paid_stack_issues() -> list[str]:
    """Return config/login gaps when paid stack is required."""
    issues: list[str] = []
    if not settings.require_paid_stack:
        return issues

    if settings.tts_provider.strip().lower() == "resemble" or not settings.allow_free_tts_fallback:
        if not settings.has_resemble:
            issues.append(
                "Resemble voice clone missing — set RESEMBLE_API_KEY + RESEMBLE_VOICE_UUID "
                "in Cursor secrets (sync_secrets writes .env)"
            )

    if not settings.allow_script_timing_fallback and not settings.has_gemini and not settings.has_assemblyai:
        issues.append(
            "Transcript sync needs GEMINI_API_KEY in Cursor secrets "
            "(same key as chat + vision QC)"
        )

    if settings.vision_qc_enabled and settings.vision_qc_blocks_upload and not settings.has_gemini:
        issues.append(
            "Gemini vision QC needs GEMINI_API_KEY in Cursor secrets"
        )

    if settings.auto_upload_youtube and settings.youtube_upload_via_api:
        from shorts_bot.youtube.google_auth import credentials_configured, token_exists, upload_ready

        if not credentials_configured():
            issues.append(
                "YouTube API upload needs GOOGLE_CLIENT_ID + GOOGLE_CLIENT_SECRET in Cursor secrets"
            )
        elif not token_exists():
            issues.append(
                "YouTube upload: run once — python3 -m shorts_bot.youtube.auth_cli "
                "(Google sign-in, not Playwright)"
            )
        elif not upload_ready():
            issues.append(
                "YouTube token missing upload scope — re-run: python3 -m shorts_bot.youtube.auth_cli"
            )

    return issues


def ensure_paid_stack_ready() -> None:
    """Raise before any finish/render if paid stack is misconfigured."""
    issues = paid_stack_issues()
    if issues:
        raise RuntimeError("Paid production stack not ready:\n- " + "\n- ".join(issues))


def ensure_resemble_voice() -> None:
    """Block edge-tts when Resemble is required."""
    if settings.allow_free_tts_fallback and settings.tts_provider.strip().lower() == "edge":
        return
    if not settings.require_paid_stack and settings.tts_provider.strip().lower() != "resemble":
        return
    if not settings.has_resemble:
        raise RuntimeError(
            "Video generation requires Resemble voice clone. "
            "Set RESEMBLE_API_KEY and RESEMBLE_VOICE_UUID in Cursor secrets. "
            "Emergency only: ALLOW_FREE_TTS_FALLBACK=true"
        )


def ensure_turboscribe_segments(sync_source: str) -> None:
    """Block script-timing fallbacks when transcript timestamps are required."""
    if settings.allow_script_timing_fallback:
        return
    if sync_source in _SCRIPT_FALLBACK_SOURCES:
        raise RuntimeError(
            f"Video generation requires transcript timestamps (got '{sync_source}'). "
            "Ensure GEMINI_API_KEY is synced — then re-run finish. "
            "Emergency only: ALLOW_SCRIPT_TIMING_FALLBACK=true"
        )


def is_turboscribe_backed(sync_source: str) -> bool:
    return sync_source in _TIMESTAMP_SOURCES
