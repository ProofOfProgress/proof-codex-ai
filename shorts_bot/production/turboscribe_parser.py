from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class TranscriptSegment:
    start_seconds: float
    text: str
    label: str  # e.g. 00.07 for filenames

    @property
    def filename_stem(self) -> str:
        return self.label


_TIME_PREFIX = re.compile(
    r"^"
    r"(?:"
    r"(?P<clock>\d{1,2}:\d{2}(?::\d{2})?)"  # 0:07 or 1:03:45
    r"|(?P<decimal>0?\.\d{2,3})"  # 0.07 = 7 sec style
    r"|(?P<plain>\d+(?:\.\d+)?)\s*(?:seconds?|sec|s)\b"  # 7 seconds
    r")"
    r"\s*",
    re.I,
)


def _clock_to_seconds(clock: str) -> float:
    parts = [int(p) for p in clock.split(":")]
    if len(parts) == 2:
        m, s = parts
        return m * 60 + s
    if len(parts) == 3:
        h, m, s = parts
        return h * 3600 + m * 60 + s
    return float(parts[0])


def _decimal_to_seconds(decimal: str) -> float:
    # Tutorial style: 0.07 often means 7 seconds (not 0.07s)
    raw = decimal.lstrip("0.") or "0"
    if "." in decimal and decimal.startswith("0."):
        # 0.07 → 7, 0.15 → 15, 0.23 → 23
        return float(raw) if raw else 0.0
    return float(decimal)


def label_from_seconds(seconds: float) -> str:
    """CapCut filename style: 00.07 = 7s, 01.03 = 1m 3s."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}.{secs:02d}"


def parse_timestamp_token(token: str) -> float | None:
    token = token.strip()
    m = re.match(
        r"^(?:(\d{1,2}):(\d{2})(?::(\d{2}))?|0\.(\d{2,3})|(\d+(?:\.\d+)?)\s*(?:s|sec|seconds)?)$",
        token,
        re.I,
    )
    if not m:
        return None
    if m.group(1) is not None:
        if m.group(3):
            return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
        return int(m.group(1)) * 60 + int(m.group(2))
    if m.group(4):
        return float(m.group(4))
    if m.group(5):
        val = float(m.group(5))
        return val
    return None


def parse_turboscribe(text: str) -> list[TranscriptSegment]:
    """
    Parse TurboScribe export or pasted transcript with timestamps.

    Supports lines like:
    - 0:07 Imagine waking up...
    - 0:07 7 seconds Imagine waking up...
    - 0.07 Imagine waking up...
    - [00:07] Imagine waking up...
    """
    if not text.strip():
        return []

    segments: list[TranscriptSegment] = []
    # Join broken lines: timestamp at start of chunk
    chunks = re.split(r"(?=\n?\d{1,2}:\d{2}|\n?0\.\d{2}|\n?\d+\s*seconds?)", text, flags=re.I)
    blob = text if len(chunks) <= 1 else text

    for raw_line in blob.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        # Strip chapter headers
        if line.lower().startswith("chapter "):
            continue

        line = re.sub(r"^\[(\d{1,2}:\d{2}(?::\d{2})?)\]\s*", r"\1 ", line)

        m = _TIME_PREFIX.match(line)
        if not m:
            if segments:
                segments[-1].text += " " + line
            continue

        start = 0.0
        if m.group("clock"):
            start = _clock_to_seconds(m.group("clock"))
        elif m.group("decimal"):
            start = _decimal_to_seconds(m.group("decimal"))
        elif m.group("plain"):
            start = float(m.group("plain"))

        rest = line[m.end() :].strip()
        # Remove duplicate "7 seconds" noise after clock
        rest = re.sub(r"^\d+(?:\.\d+)?\s*(?:seconds?|sec)\s*", "", rest, flags=re.I).strip()

        segments.append(
            TranscriptSegment(start_seconds=start, text=rest, label=label_from_seconds(start))
        )

    if not segments:
        return []

    # Dedupe by start time, merge text
    merged: dict[float, TranscriptSegment] = {}
    for seg in segments:
        if seg.start_seconds in merged:
            merged[seg.start_seconds].text += " " + seg.text
        else:
            merged[seg.start_seconds] = TranscriptSegment(
                start_seconds=seg.start_seconds,
                text=seg.text.strip(),
                label=label_from_seconds(seg.start_seconds),
            )

    return sorted(merged.values(), key=lambda s: s.start_seconds)
