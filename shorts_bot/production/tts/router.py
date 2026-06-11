"""Route TTS to configured provider."""

from __future__ import annotations

from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.production.tts.edge import synthesize_edge
from shorts_bot.production.tts.resemble import synthesize_resemble


def synthesize_speech(
    text: str,
    out_path: Path,
    *,
    voice: str | None = None,
    rate: str | None = None,
    pitch: str | None = None,
) -> tuple[str, str]:
    """
    Generate speech MP3 at out_path.

    Returns (provider_name, detail_message).
    """
    from shorts_bot.production.paid_stack import ensure_resemble_voice

    ensure_resemble_voice()
    provider = (settings.tts_provider or "resemble").strip().lower()
    edge_voice = voice or settings.tts_voice
    edge_rate = rate or settings.tts_rate
    edge_pitch = pitch or settings.tts_pitch
    if provider == "resemble" and settings.has_resemble:
        return synthesize_resemble(text, out_path)
    if settings.allow_free_tts_fallback and (provider == "edge" or not settings.has_resemble):
        if settings.tts_horror_delivery and not text.lstrip().startswith("<speak"):
            from shorts_bot.production.tts.edge_horror import synthesize_horror_edge

            return synthesize_horror_edge(text, out_path, voice=edge_voice)
        return synthesize_edge(text, out_path, voice=edge_voice, rate=edge_rate, pitch=edge_pitch)
    if settings.has_resemble:
        return synthesize_resemble(text, out_path)
    raise RuntimeError(
        "No TTS provider available. Configure Resemble (RESEMBLE_API_KEY + RESEMBLE_VOICE_UUID) "
        "or set ALLOW_FREE_TTS_FALLBACK=true for edge-tts."
    )
