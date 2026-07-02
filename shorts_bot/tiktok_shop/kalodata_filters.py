"""Kalodata UI filter presets — owner pastes saved filter URLs once."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from shorts_bot.config import settings

DEFAULT_PRESETS = (
    "middle_core",
    "two_hundred",
    "hardcore_lurkers",
    "hundred_gap",
)


def filters_path() -> Path:
    custom = (getattr(settings, "kalodata_filters_path", None) or "").strip()
    if custom:
        return Path(custom)
    return settings.data_dir / "tiktok_shop" / "kalodata_filters.json"


def load_config() -> dict[str, Any]:
    path = filters_path()
    if not path.is_file():
        return {"version": 1, "region": "US", "presets": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {"version": 1, "region": "US", "presets": {}}


def preset_block(preset: str) -> dict[str, Any]:
    presets = load_config().get("presets") or {}
    block = presets.get(preset) if isinstance(presets, dict) else None
    return block if isinstance(block, dict) else {}


def preset_filter_url(preset: str) -> str:
    url = str(preset_block(preset).get("filter_url") or "").strip()
    return url


def _is_list_filter_url(url: str) -> bool:
    """Reject product detail URLs mistakenly pasted as filter presets."""
    lower = url.lower()
    if not lower.startswith("http"):
        return False
    if "/product/detail" in lower or "id=" in lower and "/product?" not in lower:
        return False
    return "/product" in lower or "filter" in lower or "rank" in lower


def preset_has_url(preset: str) -> bool:
    url = preset_filter_url(preset)
    return bool(url) and _is_list_filter_url(url)


def hub_ui_ready(*, preset: str | None = None) -> bool:
    if preset:
        return preset_has_url(preset)
    presets = load_config().get("presets") or {}
    if not isinstance(presets, dict):
        return False
    return any(str((v or {}).get("filter_url") or "").strip() for v in presets.values() if isinstance(v, dict))


def missing_presets() -> list[str]:
    presets = load_config().get("presets") or {}
    if not isinstance(presets, dict):
        return list(DEFAULT_PRESETS)
    out: list[str] = []
    for name in DEFAULT_PRESETS:
        block = presets.get(name)
        if not isinstance(block, dict) or not str(block.get("filter_url") or "").strip():
            out.append(name)
    return out


def products_fallback_url() -> str:
    return str(load_config().get("products_page") or "https://www.kalodata.com/product").strip()
