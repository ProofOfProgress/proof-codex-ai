"""Validate MP4 files for browser preview — skip corrupt / in-progress Blender writes."""

from __future__ import annotations

import subprocess
from pathlib import Path


def is_browser_playable_mp4(path: Path, *, min_bytes: int = 50_000) -> bool:
    """True if ffprobe sees duration and moov atom (not a partial Blender frame dump)."""
    if not path.is_file() or path.stat().st_size < min_bytes:
        return False
    if "0001-" in path.name and not path.name.endswith("_01.mp4"):
        # blender_part_010001-0240.mp4 — in-progress or orphan partial
        return False
    proc = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "csv=p=0", str(path),
        ],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return False
    try:
        return float((proc.stdout or "").strip()) > 0.5
    except ValueError:
        return False


def list_playable_clips(clips_dir: Path) -> list[Path]:
    if not clips_dir.is_dir():
        return []
    out = [p for p in sorted(clips_dir.glob("*.mp4")) if is_browser_playable_mp4(p)]
    # Prefer wave test clip and numbered parts over kling leftovers
    def _sort_key(p: Path) -> tuple[int, str]:
        name = p.name
        if "wave" in name:
            return (0, name)
        if name.startswith("blender_part_") and "0001" not in name:
            return (1, name)
        return (2, name)
    return sorted(out, key=_sort_key)
