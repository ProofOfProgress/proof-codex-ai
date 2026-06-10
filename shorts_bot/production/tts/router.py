"""Route TTS to configured provider."""

from __future__ import annotations

from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.production.tts.edge import synthesize_edge
from shorts_bot.production.tts.resemble import synthesize_resemble


def synthesize_speech(text: str, out_path: Path) -> tuple[str, str]:
    """
    Generate speech MP3 at out_path.

    Returns (provider_name, detail_message).
    """
    from shorts_bot.production.paid_stack import ensure_resemble_voice

    ensure_resemble_voice()
    provider = (settings.tts_provider or "resemble").strip().lower()
    if provider == "resemble" and settings.has_resemble:
        return synthesize_resemble(text, out_path)
    if settings.allow_free_tts_fallback and (provider == "edge" or not settings.has_resemble):
        voice = settings.tts_voice
        return synthesize_edge(text, out_path, voice=voice, rate=settings.tts_rate, pitch=settings.tts_pitch)
    if settings.has_resemble:
        return synthesize_resemble(text, out_path)
    raise RuntimeError(
        "No TTS provider available. Configure Resemble (RESEMBLE_API_KEY + RESEMBLE_VOICE_UUID) "
        "or set ALLOW_FREE_TTS_FALLBACK=true for edge-tts."
    )
