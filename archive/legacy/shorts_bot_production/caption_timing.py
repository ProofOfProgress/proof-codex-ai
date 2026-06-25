"""Caption timeline — voice-synced, independent of visual segment cuts."""

from __future__ import annotations

from pathlib import Path

from shorts_bot.production.script_segments import _split_script
from shorts_bot.production.segment_sync import (
    load_cached_turboscribe_text,
    normalize_segment_timeline,
)
from shorts_bot.production.turboscribe_parser import TranscriptSegment, parse_turboscribe


def _rows_from_transcript(
    segments: list[TranscriptSegment],
    audio_duration: float,
) -> list[dict]:
    """Fine-grained TurboScribe lines → caption rows (end = next line start)."""
    if not segments:
        return []
    rows: list[dict] = []
    for i, seg in enumerate(segments):
        end = (
            segments[i + 1].start_seconds
            if i + 1 < len(segments)
            else max(audio_duration, seg.start_seconds + 0.5)
        )
        rows.append(
            {
                "start_seconds": float(seg.start_seconds),
                "end_seconds": float(end),
                "spoken_text": seg.text.strip(),
            }
        )
    return normalize_segment_timeline(rows, audio_duration)


def _rows_from_script_voice(script: str, audio_duration: float) -> list[dict]:
    """Script sentences scaled by word count to MP3 length — not visual beat count."""
    chunks = _split_script(script)
    if not chunks or audio_duration <= 0:
        return []
    weights = [max(1, len(c.split())) for c in chunks]
    total = sum(weights) or 1
    rows: list[dict] = []
    t = 0.0
    for i, chunk in enumerate(chunks):
        share = weights[i] / total
        dur = max(0.45, share * audio_duration)
        end = min(audio_duration, t + dur) if i < len(chunks) - 1 else audio_duration
        rows.append(
            {
                "start_seconds": t,
                "end_seconds": max(t + 0.08, end),
                "spoken_text": chunk.strip(),
            }
        )
        t = end
    if rows:
        rows[-1]["end_seconds"] = audio_duration
    return rows


def _apply_script_text(rows: list[dict], script: str) -> list[dict]:
    """Map approved script words onto voice-timed rows (counts may differ)."""
    if not script.strip() or not rows:
        return rows
    words: list[str] = []
    for chunk in _split_script(script):
        words.extend(chunk.split())
    if not words:
        return rows

    n = len(rows)
    out: list[dict] = []
    wi = 0
    for i in range(n):
        start_idx = int(round(i * len(words) / n))
        end_idx = int(round((i + 1) * len(words) / n))
        end_idx = max(end_idx, start_idx + 1) if i < n - 1 else len(words)
        chunk_words = words[start_idx:end_idx]
        merged = dict(rows[i])
        if chunk_words:
            merged["spoken_text"] = " ".join(chunk_words)
        out.append(merged)
    return out


def resolve_caption_segments(
    *,
    pack_dir: Path,
    script: str = "",
    audio_duration: float,
) -> list[dict]:
    """
    Caption-only timeline synced to voice — NOT tied to manifest visual cuts.

    Prefer fine-grained TurboScribe timestamps; fall back to script word pacing.
    """
    if audio_duration <= 0:
        return []

    text = load_cached_turboscribe_text(pack_dir)
    if text:
        parsed = parse_turboscribe(text)
        if parsed and len(parsed) >= 2:
            rows = _rows_from_transcript(parsed, audio_duration)
            return _apply_script_text(rows, script)

    if script.strip():
        return _rows_from_script_voice(script, audio_duration)

    return []
