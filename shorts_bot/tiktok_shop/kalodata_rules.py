"""Kalodata filter presets from guru playbooks (manual apply in UI for now)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class KalodataPreset:
    name: str
    date_range: str
    revenue_growth_min: int
    creator_max: int
    commission_min: int | None = None
    notes: str = ""


PRESET_200_METHOD = KalodataPreset(
    name="200 method",
    date_range="yesterday",
    revenue_growth_min=200,
    creator_max=150,
    notes="Hot movers — reject if no purple ad videos or brand-only creators",
)

PRESET_MIDDLE_CORE = KalodataPreset(
    name="middle core",
    date_range="last_7_days",
    revenue_growth_min=50,
    creator_max=200,
    commission_min=20,
    notes="Stronger default — need 6/10 top videos with ad badge",
)

PRODUCT_CHECKS = (
    "Top videos: 6+ of 10 have purple ad icon (GMV Max)",
    "Creator list: variety — not only the brand shop",
    "Commission $: price × rate worth posting (not $1/sale unless huge volume)",
    "Shop name matches product brand — skip random-letter Chinese sellers",
    "Captions: urgency + free shipping — NEVER specific % off",
)
