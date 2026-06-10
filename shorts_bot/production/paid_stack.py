"""Enforce paid production stack — Resemble voice + API/browser transcript sync."""

from __future__ import annotations

from shorts_bot.config import settings

_TIMESTAMP_SOURCES = frozenset({"turboscribe", "cache", "assemblyai"})
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
                "(or ALLOW_FREE_TTS_FALLBACK=true to use edge-tts)"
            )

    provider = (settings.transcript_provider or "assemblyai").strip().lower()
    if not settings.allow_script_timing_fallback:
        if provider == "assemblyai" and not settings.has_assemblyai:
            issues.append(
                "AssemblyAI transcript missing — set ASSEMBLYAI_API_KEY "
                "(or TRANSCRIPT_PROVIDER=turboscribe + TurboScribe login)"
            )
        elif provider == "turboscribe" and not settings.use_turboscribe_sync:
            issues.append(
                "TurboScribe sync disabled — set USE_TURBOSCRIBE_SYNC=true "
                "(paid Unlimited + login_handoff --only turboscribe)"
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
            "Set RESEMBLE_API_KEY and RESEMBLE_VOICE_UUID in .env, then sync_secrets. "
            "Emergency only: ALLOW_FREE_TTS_FALLBACK=true"
        )


def ensure_turboscribe_segments(sync_source: str) -> None:
    """Block script-timing fallbacks when API/browser timestamps are required."""
    if settings.allow_script_timing_fallback:
        return
    if sync_source in _SCRIPT_FALLBACK_SOURCES:
        provider = (settings.transcript_provider or "assemblyai").strip().lower()
        hint = (
            "Set ASSEMBLYAI_API_KEY (TRANSCRIPT_PROVIDER=assemblyai)"
            if provider == "assemblyai"
            else "Log in: python3 -m shorts_bot.login_handoff --only turboscribe"
        )
        raise RuntimeError(
            f"Video generation requires word-level transcript timestamps (got '{sync_source}'). "
            f"{hint} — then re-run finish. Emergency only: ALLOW_SCRIPT_TIMING_FALLBACK=true"
        )


def is_turboscribe_backed(sync_source: str) -> bool:
    return sync_source in _TIMESTAMP_SOURCES
