"""Voiceover generation — Resemble voice clone (paid) or edge-tts fallback."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

DEFAULT_VOICE = "en-US-AriaNeural"
ALT_VOICES = (
    "en-US-AriaNeural",
    "en-US-JennyNeural",
    "en-GB-SoniaNeural",
    "en-US-BrianNeural",
)


@dataclass
class VoiceoverResult:
    draft_id: int
    output_path: Path
    voice: str
    duration_hint: str
    message: str


def _clean_script_for_tts(text: str) -> str:
    """Strip markdown headers and stage directions."""
    lines = []
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("---") or s.startswith("HOOK:"):
            continue
        if s.startswith("#"):
            continue
        lines.append(s)
    body = " ".join(lines)
    body = re.sub(r"\s+", " ", body).strip()
    return body


def _voiceover_path(pack_dir: Path) -> Path:
    return pack_dir / "voiceover.mp3"


def generate_voiceover(
    pack_dir: Path,
    *,
    draft_id: int,
    script_text: str,
    voice: str | None = None,
    rate: str | None = None,
    pitch: str | None = None,
) -> VoiceoverResult:
    """
    Generate MP3 voiceover into production pack folder.

    Default: Resemble voice clone when RESEMBLE_API_KEY + RESEMBLE_VOICE_UUID are set.
    Fallback: edge-tts (free).
    """
    from shorts_bot.config import settings
    from shorts_bot.production.tts import synthesize_speech

    pack_dir.mkdir(parents=True, exist_ok=True)
    spoken = _clean_script_for_tts(script_text)
    if len(spoken) < 20:
        raise ValueError("Script too short for voiceover generation.")

    out_path = _voiceover_path(pack_dir)
    provider, detail = synthesize_speech(spoken, out_path)

    voice_label = voice or settings.tts_voice or DEFAULT_VOICE
    if provider == "resemble-clone":
        voice_label = f"resemble:{settings.resemble_voice_uuid[:8]}…"

    word_count = len(spoken.split())
    secs = max(25, int(word_count / 2.4))

    return VoiceoverResult(
        draft_id=draft_id,
        output_path=out_path,
        voice=voice_label,
        duration_hint=f"~{secs}s at calm pace",
        message=detail,
    )


def list_voices() -> list[str]:
    return list(ALT_VOICES)
