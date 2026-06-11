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
    use_horror = settings.tts_horror_delivery
    provider_name = (settings.tts_provider or "resemble").strip().lower()
    use_edge = provider_name == "edge" or (
        settings.allow_free_tts_fallback and not settings.has_resemble
    ) or (settings.allow_free_tts_fallback and provider_name != "resemble")

    if use_horror and use_edge:
        from shorts_bot.production.tts.edge_horror import synthesize_horror_edge

        (pack_dir / "voiceover_delivery.txt").write_text(
            f"horror edge pacing ({len(spoken.split())} words)\n{spoken}",
            encoding="utf-8",
        )
        provider, detail = synthesize_horror_edge(
            spoken,
            out_path,
            voice=voice or settings.tts_voice,
        )
    else:
        tts_input = spoken
        if use_horror and not use_edge:
            from shorts_bot.production.tts.horror_voice import prepare_horror_resemble_ssml

            prompt = (settings.resemble_horror_prompt or "").strip() or None
            tts_input = prepare_horror_resemble_ssml(spoken, prompt=prompt)
            (pack_dir / "voiceover_ssml.txt").write_text(tts_input, encoding="utf-8")

        provider, detail = synthesize_speech(
            tts_input,
            out_path,
            rate=rate or settings.tts_rate,
            pitch=pitch or settings.tts_pitch,
            voice=voice or settings.tts_voice,
        )

    voice_label = voice or settings.tts_voice or DEFAULT_VOICE
    if provider == "resemble-clone":
        voice_label = f"resemble:{settings.resemble_voice_uuid[:8]}…"

    word_count = len(spoken.split())
    secs = max(25, int(word_count / 2.4))
    delivery = " (horror dread pacing)" if settings.tts_horror_delivery else ""

    return VoiceoverResult(
        draft_id=draft_id,
        output_path=out_path,
        voice=voice_label,
        duration_hint=f"~{secs}s at dread pace",
        message=detail + delivery,
    )


def list_voices() -> list[str]:
    return list(ALT_VOICES)
