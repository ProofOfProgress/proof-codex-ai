"""Video variants — 5s forward + reverse = ~10s (not identical dupes)."""

from __future__ import annotations

import subprocess
from pathlib import Path


def make_pan_loop_clip(source: Path, dest: Path) -> Path:
    """
    Concatenate source + reversed source for a ~2× length loop.
    Requires ffmpeg on PATH.
    """
    if not source.is_file():
        raise FileNotFoundError(source)
    dest.parent.mkdir(parents=True, exist_ok=True)
    rev = dest.with_name(dest.stem + "_rev.mp4")
    cmd_rev = [
        "ffmpeg", "-y", "-i", str(source),
        "-vf", "reverse",
        "-an", str(rev),
    ]
    subprocess.run(cmd_rev, check=True, capture_output=True)

    list_file = dest.with_suffix(".txt")
    list_file.write_text(f"file '{source.resolve()}'\nfile '{rev.resolve()}'\n", encoding="utf-8")
    cmd_cat = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(list_file),
        "-c", "copy",
        str(dest),
    ]
    subprocess.run(cmd_cat, check=True, capture_output=True)
    if rev.is_file():
        rev.unlink(missing_ok=True)
    list_file.unlink(missing_ok=True)
    return dest
