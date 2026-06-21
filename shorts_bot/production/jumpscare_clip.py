"""Retired jumpscare clip — stubs."""

from __future__ import annotations

from pathlib import Path


def jumpscare_clip_path(clips_dir: Path) -> Path:
    return clips_dir / "jumpscare_lunge.mp4"


def jumpscare_clip_is_valid(pack_dir: Path, clips_dir: Path) -> bool:
    return False


def ensure_jumpscare_video_clip(*args, **kwargs):
    return None
