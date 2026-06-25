"""Pick the best finished Short MP4 from a draft production pack."""

from __future__ import annotations

import re
from pathlib import Path

# QA / iteration filenames — deprioritize for public or compilation use.
_DEPRIORITIZE_SUBSTRINGS = (
    "sync_test",
    "unlisted",
    "_regen",
    "align",
    "scrub",
    "_fixed",
    "_ui",
    "jumpscare_clip",
    "voice_caps",
)

_BUILD_SUFFIX_RE = re.compile(r"\(build\s+v\d+", re.I)


def resolve_final_short_video(
    pack_dir: Path,
    *,
    preferred_name: str | None = None,
    exclude_qa_builds: bool = True,
) -> Path | None:
    """Return newest suitable final_short*.mp4, or None."""
    if not pack_dir.is_dir():
        return None

    if preferred_name:
        preferred = pack_dir / preferred_name
        if preferred.is_file() and preferred.stat().st_size > 5000:
            return preferred

    candidates: list[Path] = []
    for path in pack_dir.glob("final_short*.mp4"):
        if path.stat().st_size < 5000:
            continue
        name = path.name.lower()
        if exclude_qa_builds and any(tag in name for tag in _DEPRIORITIZE_SUBSTRINGS):
            continue
        candidates.append(path)

    if not candidates:
        for path in pack_dir.glob("final_short*.mp4"):
            if path.stat().st_size >= 5000:
                candidates.append(path)

    if not candidates:
        fallback = pack_dir / "final_short.mp4"
        return fallback if fallback.is_file() else None

    return max(candidates, key=lambda p: p.stat().st_mtime)


def is_qa_build_filename(name: str) -> bool:
    lower = name.lower()
    if _BUILD_SUFFIX_RE.search(name):
        return True
    return any(tag in lower for tag in _DEPRIORITIZE_SUBSTRINGS)
