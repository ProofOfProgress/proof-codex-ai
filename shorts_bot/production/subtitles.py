"""Segment subtitles — SRT + ASS for burn-in (Jenny 05: mute-safe + safe zone)."""

from __future__ import annotations

import textwrap
from pathlib import Path

from shorts_bot.production.framing import SUBTITLE_FONT_SIZE, SUBTITLE_MARGIN_V_PX


def _fmt_srt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds % 1) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _fmt_ass_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def _wrap_caption(text: str, width: int = 32) -> str:
    t = " ".join(text.split())
    if len(t) <= width:
        return t
    return "\n".join(textwrap.wrap(t, width=width))


def build_subtitles_from_manifest(
    segments: list[dict],
    *,
    audio_duration: float,
) -> tuple[str, str]:
    """Return (srt_content, ass_content) timed to audio length."""
    manifest_total = segments[-1]["end_seconds"] if segments else 1.0
    scale = audio_duration / manifest_total if manifest_total > 0 else 1.0

    srt_lines: list[str] = []
    ass_events: list[str] = []
    idx = 1

    for seg in segments:
        start = seg["start_seconds"] * scale
        end = seg["end_seconds"] * scale
        text = _wrap_caption(seg.get("spoken_text", "").strip())
        if not text:
            continue
        srt_lines.append(str(idx))
        srt_lines.append(f"{_fmt_srt_time(start)} --> {_fmt_srt_time(end)}")
        srt_lines.append(text)
        srt_lines.append("")
        ass_events.append(
            f"Dialogue: 0,{_fmt_ass_time(start)},{_fmt_ass_time(end)},Default,,0,0,0,,{text.replace(chr(10), r'\N')}"
        )
        idx += 1

    srt = "\n".join(srt_lines)
    ass = f"""[Script Info]
Title: Soft Continuity
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,DejaVu Sans Bold,{SUBTITLE_FONT_SIZE},&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,1,2,60,60,{SUBTITLE_MARGIN_V_PX},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ass += "\n".join(ass_events) + "\n"
    return srt, ass


def write_subtitle_files(pack_dir: Path, segments: list[dict], audio_duration: float) -> Path:
    srt, ass = build_subtitles_from_manifest(segments, audio_duration=audio_duration)
    (pack_dir / "captions.srt").write_text(srt, encoding="utf-8")
    ass_path = pack_dir / "subtitles.ass"
    ass_path.write_text(ass, encoding="utf-8")
    return ass_path
