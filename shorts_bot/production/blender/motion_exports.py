"""Proscenium / Mixamo motion FBX exports — owner drops files here for cloud render."""

from __future__ import annotations

import re
from pathlib import Path

PHASES = ("open", "wave", "lunge")


def motion_exports_dir() -> Path:
    root = Path(__file__).resolve().parents[3]
    return root / "channel" / "assets" / "motion_exports"


def draft_id_from_pack(pack_dir: Path) -> int | None:
    m = re.match(r"draft_(\d+)", pack_dir.name)
    return int(m.group(1)) if m else None


def motion_fbx_candidates(draft_id: int, phase: str) -> list[Path]:
    """Naming patterns owners may use after Proscenium export."""
    phase = phase if phase in PHASES else "wave"
    root = motion_exports_dir()
    names = (
        f"draft_{draft_id}_{phase}.fbx",
        f"draft_{draft_id}_{phase}_proscenium.fbx",
        f"draft{draft_id}_{phase}.fbx",
        f"{phase}_draft_{draft_id}.fbx",
        f"draft_{draft_id}_{phase}.blend",
    )
    return [root / n for n in names]


def resolve_motion_fbx(draft_id: int, phase: str) -> Path | None:
    """Return first existing Proscenium/Mixamo export for this draft clip."""
    for path in motion_fbx_candidates(draft_id, phase):
        if path.is_file() and path.stat().st_size > 500:
            return path
    return None


def list_motion_exports(draft_id: int) -> dict[str, Path]:
    """Which phases have owner-exported motion on disk."""
    return {phase: p for phase in PHASES if (p := resolve_motion_fbx(draft_id, phase))}
