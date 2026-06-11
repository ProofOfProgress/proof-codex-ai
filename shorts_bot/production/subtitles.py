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
from shorts_bot.production.script_segments import _split_script


def _merge_chunks_to_count(chunks: list[str], target: int) -> list[str]:
    """Merge script sentences until count matches visual segment count."""
    if target <= 0 or not chunks:
        return chunks
    merged = list(chunks)
    while len(merged) > target:
        best_i = 0
        best_len = len(merged[0]) + len(merged[1])
        for i in range(len(merged) - 1):
            pair_len = len(merged[i]) + len(merged[i + 1])
            if pair_len < best_len:
                best_len = pair_len
                best_i = i
        merged[best_i : best_i + 2] = [f"{merged[best_i]} {merged[best_i + 1]}".strip()]
    return merged


def caption_text_for_segments(
    segments: list[dict],
    *,
    script: str | None = None,
) -> list[str]:
    """Prefer approved script lines over TurboScribe spoken_text (ASR typos)."""
    n = len(segments)
    if not script or not script.strip():
        return [str(s.get("spoken_text", "")).strip() for s in segments]
    chunks = _merge_chunks_to_count(_split_script(script), n)
    if len(chunks) != n:
        return [str(s.get("spoken_text", "")).strip() for s in segments]
    return chunks


def _timeline_scale(segments: list[dict], audio_duration: float) -> float:
    """Return 1.0 when segments are already normalized to audio_duration."""
    if not segments or audio_duration <= 0:
        return 1.0
    first = float(segments[0].get("start_seconds", 0))
    last = float(segments[-1].get("end_seconds", 0))
    if first < 0.15 and abs(last - audio_duration) < 0.35:
        return 1.0
    manifest_total = last if last > 0 else 1.0
    return audio_duration / manifest_total


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
Title: Don't Blink
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
    script: str | None = None,
) -> tuple[str, str]:
    """Return (srt_content, ass_content) timed to scaled audio."""
    scale = _timeline_scale(segments, audio_duration)
    caption_lines = caption_text_for_segments(segments, script=script)

    srt_lines: list[str] = []
    ass_events: list[str] = []
    idx = 1

    margin_tag = ass_force_margin_override(y_offset=caption_y_offset)

    for seg, raw in zip(segments, caption_lines):
        start = seg["start_seconds"] * scale
        end = max(start + 0.08, seg["end_seconds"] * scale)
        raw = raw.strip()
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
    script: str | None = None,
) -> Path:
    if script is None:
        manifest_path = pack_dir / "manifest.json"
        if manifest_path.exists():
            try:
                import json

                script = json.loads(manifest_path.read_text(encoding="utf-8")).get("script")
            except (json.JSONDecodeError, OSError):
                script = None
    srt, ass = build_subtitles_from_manifest(
        segments,
        audio_duration=audio_duration,
        caption_y_offset=caption_y_offset,
        script=script,
    )
    (pack_dir / "captions.srt").write_text(srt, encoding="utf-8")
    ass_path = pack_dir / "subtitles.ass"
    ass_path.write_text(ass, encoding="utf-8")
    return ass_path


def ffmpeg_subtitles_filter(ass_path: Path) -> str:
    """Build ffmpeg -vf filter chain for ASS burn-in."""
    escaped = str(ass_path.resolve()).replace("\\", "/").replace(":", r"\:")
    return f"format=yuv420p,subtitles='{escaped}'"
