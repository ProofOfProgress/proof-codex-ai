"""Resolve AV segment timing — TurboScribe, SRT cache, script scaled to MP3."""

from __future__ import annotations

from pathlib import Path

from shorts_bot.production.script_segments import (
    segments_from_script,
    segments_from_script_for_duration,
)
from shorts_bot.production.turboscribe_parser import TranscriptSegment, parse_turboscribe


def merge_segments_for_visual_cuts(
    segments: list[TranscriptSegment],
    *,
    target_min_seconds: float = 2.0,
    target_max_seconds: float = 5.5,
    audio_duration: float | None = None,
) -> list[TranscriptSegment]:
    """Merge fine-grained TS segments into ChainsFR-style ~2–5s visual cuts."""
    if len(segments) <= 1:
        return segments

    from shorts_bot.production.turboscribe_parser import label_from_seconds

    merged: list[TranscriptSegment] = []
    start = segments[0].start_seconds
    texts: list[str] = []

    for i, seg in enumerate(segments):
        texts.append(seg.text.strip())
        next_start = segments[i + 1].start_seconds if i + 1 < len(segments) else None
        span = (next_start - start) if next_start is not None else target_min_seconds
        words = sum(len(t.split()) for t in texts)
        last = i == len(segments) - 1
        flush = last or span >= target_max_seconds or (span >= target_min_seconds and words >= 6)
        if flush:
            text = " ".join(texts).strip()
            if text:
                merged.append(
                    TranscriptSegment(
                        start_seconds=start,
                        text=text,
                        label=label_from_seconds(start),
                    )
                )
            if not last:
                start = segments[i + 1].start_seconds
                texts = []

    if audio_duration and len(merged) >= 2:
        span = merged[-1].start_seconds - merged[0].start_seconds
        if span > 0 and abs(span - audio_duration) > 1.5:
            scale = audio_duration / span
            base = merged[0].start_seconds
            merged = [
                TranscriptSegment(
                    start_seconds=base + (s.start_seconds - base) * scale,
                    text=s.text,
                    label=label_from_seconds(base + (s.start_seconds - base) * scale),
                )
                for s in merged
            ]
    return merged


def load_cached_turboscribe_text(pack_dir: Path) -> str:
    for name in ("transcript.txt", "turboscribe_transcript.txt", "turboscribe.txt"):
        path = pack_dir / name
        if path.exists():
            text = path.read_text(encoding="utf-8").strip()
            if text:
                return text
    return ""


def resolve_segments(
    *,
    script: str,
    pack_dir: Path,
    turboscribe_text: str = "",
    audio_duration: float | None = None,
) -> tuple[list[TranscriptSegment], str]:
    """
    Pick best segment source. Returns (segments, source_label).
    source_label: turboscribe | cache | script_duration | script_estimate
    """
    text = turboscribe_text.strip() or load_cached_turboscribe_text(pack_dir)
    if text:
        parsed = parse_turboscribe(text)
        if parsed:
            if len(parsed) > 12:
                parsed = merge_segments_for_visual_cuts(parsed, audio_duration=audio_duration)
            return parsed, "turboscribe" if turboscribe_text.strip() else "cache"

    audio_path = pack_dir / "voiceover.mp3"
    if audio_path.exists() and audio_duration is None:
        from shorts_bot.production.render_video import _probe_duration

        try:
            audio_duration = _probe_duration(audio_path)
        except Exception:
            audio_duration = None

    if audio_duration and audio_duration > 0:
        return segments_from_script_for_duration(script, audio_duration), "script_duration"

    return segments_from_script(script), "script_estimate"
