"""Optional voiceover generation — free local neural TTS (edge-tts)."""

from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass
from pathlib import Path

# Calm, warm voices suited to Soft Continuity (Microsoft Edge neural, free).
DEFAULT_VOICE = "en-US-AriaNeural"
ALT_VOICES = (
    "en-US-AriaNeural",
    "en-US-JennyNeural",
    "en-GB-SoniaNeural",
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


async def _synthesize(text: str, out_path: Path, voice: str) -> None:
    import edge_tts

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(out_path))


def generate_voiceover(
    pack_dir: Path,
    *,
    draft_id: int,
    script_text: str,
    voice: str = DEFAULT_VOICE,
) -> VoiceoverResult:
    """
    Generate MP3 voiceover into production pack folder.

    Uses edge-tts (free, no login). Not uploaded anywhere — local file only.
    """
    pack_dir.mkdir(parents=True, exist_ok=True)
    spoken = _clean_script_for_tts(script_text)
    if len(spoken) < 20:
        raise ValueError("Script too short for voiceover generation.")

    out_path = _voiceover_path(pack_dir)
    asyncio.run(_synthesize(spoken, out_path, voice))

    word_count = len(spoken.split())
    secs = max(25, int(word_count / 2.4))  # ~145 wpm calm pace

    return VoiceoverResult(
        draft_id=draft_id,
        output_path=out_path,
        voice=voice,
        duration_hint=f"~{secs}s at calm pace",
        message=(
            f"Voiceover saved: {out_path} ({voice}). "
            f"Import into CapCut with images/. "
            f"See VOICEOVER_POLICY.md for YouTube risk notes."
        ),
    )


def list_voices() -> list[str]:
    return list(ALT_VOICES)
