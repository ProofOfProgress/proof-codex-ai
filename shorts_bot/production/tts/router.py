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
    provider = (settings.tts_provider or "resemble").strip().lower()
    if provider == "resemble" and settings.has_resemble:
        return synthesize_resemble(text, out_path)
    if provider == "edge" or not settings.has_resemble:
        voice = settings.tts_voice
        return synthesize_edge(text, out_path, voice=voice, rate=settings.tts_rate, pitch=settings.tts_pitch)
    return synthesize_resemble(text, out_path)
