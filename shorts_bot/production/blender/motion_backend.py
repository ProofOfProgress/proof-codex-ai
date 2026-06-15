"""Motion backend policy — learned/procedural default; Mixamo download opt-in only."""

from __future__ import annotations

import os

DOWNLOAD_BACKENDS = frozenset({"proscenium_fbx", "proscenium", "mixamo"})


def use_downloaded_motion() -> bool:
    """
    True only when owner explicitly opts into Mixamo/Proscenium FBX downloads.

    Default procedural keeps the Blender self-train loop in control of motion craft.
    """
    raw = os.environ.get("BLENDER_MOTION_BACKEND", "").strip().lower()
    if raw in DOWNLOAD_BACKENDS:
        return True
    if raw == "auto":
        return os.environ.get("BLENDER_USE_MIXAMO", "").strip().lower() in ("1", "true", "yes", "on")
    return False


def resolved_motion_backend() -> str:
    """Backend string for logging and manifests."""
    if use_downloaded_motion():
        return os.environ.get("BLENDER_MOTION_BACKEND", "proscenium_fbx").strip().lower() or "proscenium_fbx"
    raw = os.environ.get("BLENDER_MOTION_BACKEND", "procedural").strip().lower()
    if raw in DOWNLOAD_BACKENDS:
        return "procedural"
    return raw or "procedural"


def motion_source_label(*, use_mixamo: bool | None = None) -> str:
    if use_mixamo is None:
        from shorts_bot.config import settings

        use_mixamo = settings.blender_use_mixamo_motion
    return "mixamo" if use_mixamo else "procedural_learned"


def motion_env(*, use_mixamo: bool | None = None) -> dict[str, str]:
    """Subprocess env fragment for Blender renders."""
    from shorts_bot.config import settings

    if use_mixamo is None:
        use_mixamo = settings.blender_use_mixamo_motion
    if use_mixamo:
        return {
            "BLENDER_MOTION_BACKEND": "proscenium_fbx",
            "BLENDER_USE_MIXAMO": "1",
        }
    backend = (settings.blender_motion_backend or "procedural").strip().lower()
    return {
        "BLENDER_MOTION_BACKEND": backend,
        "BLENDER_USE_MIXAMO": "0",
    }
