"""Minimal ffmpeg probe — shared utility (legacy render removed)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


def _probe_duration(path: Path) -> float:
    proc = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or "ffprobe failed")
    data = json.loads(proc.stdout or "{}")
    return float(data.get("format", {}).get("duration", 0))
