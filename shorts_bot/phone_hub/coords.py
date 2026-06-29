"""Calibrated tap coordinates per phone slot — fallback when uiautomator text fails."""

from __future__ import annotations

import json
from pathlib import Path

from shorts_bot.config import settings


def coords_path() -> Path:
    return settings.data_dir / "phone_hub" / "ui_coords.json"


def load_coords() -> dict:
    path = coords_path()
    if not path.is_file():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    return raw if isinstance(raw, dict) else {}


def get_coord(slot: str, key: str) -> tuple[int, int] | None:
    """Return (x, y) for slot+key — slot overrides, then _default."""
    raw = load_coords()
    slot_block = raw.get(slot) if isinstance(raw.get(slot), dict) else {}
    default_block = raw.get("_default") if isinstance(raw.get("_default"), dict) else {}
    point = slot_block.get(key) if isinstance(slot_block, dict) else None
    if point is None and isinstance(default_block, dict):
        point = default_block.get(key)
    if isinstance(point, dict) and "x" in point and "y" in point:
        return int(point["x"]), int(point["y"])
    if isinstance(point, (list, tuple)) and len(point) >= 2:
        return int(point[0]), int(point[1])
    return None
