from __future__ import annotations

import re

from shorts_bot.production.turboscribe_parser import TranscriptSegment, label_from_seconds

_WORDS_PER_SECOND = 2.4
_MIN_SEGMENT_SECONDS = 2.0  # ChainsFR / Zen case study: visual cut every ~2–3s


def _split_script(script: str) -> list[str]:
    script = re.sub(r"\s+", " ", script.strip())
    parts = re.split(r"(?<=[.!?])\s+", script)
    chunks: list[str] = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if len(p.split()) > 18:
            sub = re.split(r"(?<=[,;])\s+", p)
            chunks.extend(s.strip() for s in sub if s.strip())
        else:
            chunks.append(p)
    return chunks or [script]


def _duration_seconds(text: str) -> float:
    words = max(1, len(text.split()))
    return max(_MIN_SEGMENT_SECONDS, words / _WORDS_PER_SECOND)


def segments_from_script(script: str) -> list[TranscriptSegment]:
    """Estimate TurboScribe-style timestamps from approved script (no audio needed)."""
    return _build_segments(_split_script(script))


def segments_from_script_for_duration(script: str, audio_duration: float) -> list[TranscriptSegment]:
    """Scale sentence cuts to match real voiceover length — tighter AV sync fallback."""
    chunks = _split_script(script)
    if not chunks or audio_duration <= 0:
        return segments_from_script(script)
    raw = [_duration_seconds(c) for c in chunks]
    total = sum(raw) or 1.0
    scale = audio_duration / total
    durations = [max(_MIN_SEGMENT_SECONDS, d * scale) for d in raw]
    fix = audio_duration / sum(durations)
    durations = [d * fix for d in durations]
    return _build_segments(chunks, durations=durations)


def _build_segments(
    chunks: list[str],
    *,
    durations: list[float] | None = None,
) -> list[TranscriptSegment]:
    segments: list[TranscriptSegment] = []
    t = 0.0
    for i, chunk in enumerate(chunks):
        dur = durations[i] if durations else _duration_seconds(chunk)
        segments.append(
            TranscriptSegment(start_seconds=t, text=chunk, label=label_from_seconds(t))
        )
        t += dur
    return segments
