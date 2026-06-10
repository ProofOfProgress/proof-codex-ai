"""Segment subtitles — SRT + ASS for ffmpeg burn-in (Jenny 05 safe zone)."""

from __future__ import annotations

from pathlib import Path

from shorts_bot.production.captions import (
    ass_force_margin_override,
    caption_display_text,
    escape_ass_text,
    format_caption_lines,
)
from shorts_bot.production.framing import (
    CAPTION_SIDE_MARGIN_PX,
    FRAME_HEIGHT,
    FRAME_WIDTH,
    SUBTITLE_FONT_SIZE,
    SUBTITLE_MARGIN_V_PX,
)


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


def _ass_header() -> str:
    # BorderStyle 3 = opaque box behind text (TikTok-style bar via libass)
    # MarginV + \pos override = Jenny 05 safe zone above Shorts title UI
    return f"""[Script Info]
Title: Soft Continuity
ScriptType: v4.00+
PlayResX: {FRAME_WIDTH}
PlayResY: {FRAME_HEIGHT}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,DejaVu Sans,{SUBTITLE_FONT_SIZE},&H00FFFFFF,&H000000FF,&H00000000,&HC0000000,-1,0,0,0,100,100,0,0,3,2,0,2,{CAPTION_SIDE_MARGIN_PX},{CAPTION_SIDE_MARGIN_PX},{SUBTITLE_MARGIN_V_PX},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def build_subtitles_from_manifest(
    segments: list[dict],
    *,
    audio_duration: float,
    caption_y_offset: int = 0,
) -> tuple[str, str]:
    """Return (srt_content, ass_content) timed to scaled audio."""
    manifest_total = segments[-1]["end_seconds"] if segments else 1.0
    scale = audio_duration / manifest_total if manifest_total > 0 else 1.0

    srt_lines: list[str] = []
    ass_events: list[str] = []
    idx = 1

    margin_tag = ass_force_margin_override(y_offset=caption_y_offset)

    for seg in segments:
        start = seg["start_seconds"] * scale
        end = max(start + 0.08, seg["end_seconds"] * scale)
        raw = seg.get("spoken_text", "").strip()
        if not raw:
            continue

        display = caption_display_text(raw)
        if not display:
            continue

        srt_lines.append(str(idx))
        srt_lines.append(f"{_fmt_srt_time(start)} --> {_fmt_srt_time(end)}")
        srt_lines.append(display)
        srt_lines.append("")

        ass_body = escape_ass_text(display)
        ass_events.append(
            f"Dialogue: 0,{_fmt_ass_time(start)},{_fmt_ass_time(end)},Default,,0,0,0,,"
            f"{margin_tag}{ass_body}"
        )
        idx += 1

    srt = "\n".join(srt_lines)
    ass = _ass_header() + "\n".join(ass_events) + "\n"
    return srt, ass


def write_subtitle_files(
    pack_dir: Path,
    segments: list[dict],
    audio_duration: float,
    *,
    caption_y_offset: int = 0,
) -> Path:
    srt, ass = build_subtitles_from_manifest(
        segments,
        audio_duration=audio_duration,
        caption_y_offset=caption_y_offset,
    )
    (pack_dir / "captions.srt").write_text(srt, encoding="utf-8")
    ass_path = pack_dir / "subtitles.ass"
    ass_path.write_text(ass, encoding="utf-8")
    return ass_path


def ffmpeg_subtitles_filter(ass_path: Path) -> str:
    """Build ffmpeg -vf filter chain for ASS burn-in."""
    escaped = str(ass_path.resolve()).replace("\\", "/").replace(":", r"\:")
    return f"format=yuv420p,subtitles='{escaped}'"
