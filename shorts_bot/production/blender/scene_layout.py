"""Shared scene layout — owner moves models in browser; Blender reads on render."""

from __future__ import annotations

import json
import math
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_LAYOUT: dict[str, Any] = {
    "version": 1,
    "creature": {
        "location": [0.0, -7.5, 0.0],
        "rotation": [0.0, 0.0, 0.0],
        "scale": [1.0, 1.0, 1.35],
    },
    "camera": {
        "location": [0.0, 2.0, 1.65],
        "rotation": [math.radians(88), 0.0, math.radians(180)],
        "lens": 24.0,
    },
    "environment": {"scale": 0.07, "offset_y": -6.0},
}


def scene_layout_path(pack_dir: Path) -> Path:
    return pack_dir / "scene_layout.json"


def load_scene_layout(pack_dir: Path | None, *, draft_id: int | None = None) -> dict[str, Any]:
    layout = deepcopy(DEFAULT_LAYOUT)
    if draft_id is not None:
        layout["draft_id"] = draft_id
    if pack_dir is None:
        return layout
    path = scene_layout_path(pack_dir)
    if not path.is_file():
        return layout
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return layout
    for key in ("creature", "camera", "environment"):
        if isinstance(data.get(key), dict):
            layout[key] = {**layout.get(key, {}), **data[key]}
    for key in ("version", "draft_id", "updated_at", "updated_by"):
        if key in data:
            layout[key] = data[key]
    return layout


def save_scene_layout(pack_dir: Path, layout: dict[str, Any], *, updated_by: str = "owner") -> Path:
    pack_dir.mkdir(parents=True, exist_ok=True)
    payload = deepcopy(layout)
    payload["updated_at"] = datetime.now(timezone.utc).isoformat()
    payload["updated_by"] = updated_by
    path = scene_layout_path(pack_dir)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def merge_layout_update(existing: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(existing)
    for key in ("creature", "camera", "environment"):
        if isinstance(patch.get(key), dict):
            merged[key] = {**merged.get(key, {}), **patch[key]}
    return merged


def apply_scene_layout(
    pack_dir: Path | None,
    *,
    camera: Any,
    creature: Any,
    environment: Any | None = None,
) -> dict[str, Any]:
    """Apply saved layout to Blender objects (bpy.types.Object)."""
    layout = load_scene_layout(pack_dir)
    from mathutils import Vector  # type: ignore

    c = layout.get("creature") or {}
    if loc := c.get("location"):
        creature.location = Vector(loc)
    if rot := c.get("rotation"):
        creature.rotation_euler = Vector(rot)
    if scale := c.get("scale"):
        creature.scale = Vector(scale)

    cam = layout.get("camera") or {}
    if loc := cam.get("location"):
        camera.location = Vector(loc)
    if rot := cam.get("rotation"):
        camera.rotation_euler = Vector(rot)
    if lens := cam.get("lens"):
        camera.data.lens = float(lens)

    if environment is not None:
        env = layout.get("environment") or {}
        if scale := env.get("scale"):
            s = float(scale)
            environment.scale = Vector((s, s, s))

    return layout


def creature_wave_positions(layout: dict[str, Any]) -> tuple[list[float], list[float], list[float] | None]:
    """Wave-phase start/end creature positions — layout-aware."""
    default_start = [0.0, -7.5, 0.0]
    default_end = [0.0, -6.0, 0.0]
    c = layout.get("creature") or {}
    start = list(c.get("location") or default_start)
    delta = [default_end[i] - default_start[i] for i in range(3)]
    end = [start[i] + delta[i] for i in range(3)]
    scale = c.get("scale")
    return start, end, scale
