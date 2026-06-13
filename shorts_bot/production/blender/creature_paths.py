"""Creature model paths — no bpy (safe to import in tests/CLI)."""

from __future__ import annotations

from pathlib import Path

DEFAULT_CREATURE_DIR = Path("channel/assets/creatures")
SCP096_DIR = DEFAULT_CREATURE_DIR / "scp_096"
SCP096_CANDIDATES = (
    SCP096_DIR / "scp_096.glb",
    SCP096_DIR / "scp_096.fbx",
    SCP096_DIR / "scp_096.obj",
    SCP096_DIR / "scp_096.dae",
    SCP096_DIR / "scp_096.b3d",
    DEFAULT_CREATURE_DIR / "scp_096.glb",
    DEFAULT_CREATURE_DIR / "scp_096.fbx",
)


def resolve_creature_model(explicit: str | Path | None = None) -> Path | None:
    """First existing model file — explicit path, env, or default scp_096 slot."""
    if explicit:
        p = Path(explicit)
        if p.is_file():
            return p
        if p.is_dir():
            for name in ("scp_096.fbx", "scp_096.glb", "scp_096.obj", "model.fbx", "model.glb"):
                hit = p / name
                if hit.is_file():
                    return hit
            return None
        return None
    for candidate in SCP096_CANDIDATES:
        if candidate.is_file():
            return candidate
    return None


def creature_model_status(explicit: str | Path | None = None) -> dict:
    resolved = resolve_creature_model(explicit)
    return {
        "resolved": str(resolved) if resolved else None,
        "expected_dir": str(SCP096_DIR),
        "candidates_checked": [str(c) for c in SCP096_CANDIDATES],
    }
