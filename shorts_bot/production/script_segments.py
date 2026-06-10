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
    chunks = _split_script(script)
    segments: list[TranscriptSegment] = []
    t = 0.0
    for chunk in chunks:
        segments.append(
            TranscriptSegment(start_seconds=t, text=chunk, label=label_from_seconds(t))
        )
        t += _duration_seconds(chunk)
    return segments
