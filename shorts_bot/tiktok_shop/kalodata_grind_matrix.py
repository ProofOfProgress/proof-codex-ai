"""Kalodata grind matrix: course method × category, coach high-ticket on everything."""

from __future__ import annotations

# Coach overlay (2026-06-30) — apply on EVERY scout pass
COACH_OVERLAY = {
    "avg_unit_price_min": 80,
    "commission_min_pct": 8,
    "creator_max": 200,
    "revenue_7d_min": 10000,
    "revenue_growth_min_pct": 30,
    "is_affiliate": True,
}

# Course methods (swap category only between runs)
METHODS: dict[str, dict] = {
    "hardcore": {
        "date": "yesterday",
        "revenue_growth_min_pct": 100,
        "creator_max": 200,
    },
    "lurkers": {
        "date": "last_7_days",
        "creator_min": 10,
        "creator_max": 200,
        "revenue_growth_min_pct": 10,
    },
    "hundred_gap": {
        "date": "yesterday",
        "revenue_min": 100,
        "revenue_max": 1000,
        "items_sold_min": 50,
        "items_sold_max": 500,
        "creator_max": 250,
    },
    "middle_core": {
        "date": "last_7_days",
        "revenue_growth_min_pct": 50,
        "creator_max": 200,
        "commission_min_pct": 20,
    },
    "two_hundred": {
        "date": "yesterday",
        "revenue_growth_min_pct": 100,
        "creator_max": 200,
    },
}

# Rotate categories — coach said try everything, not one preset forever
LAUNCH_CATEGORIES: tuple[str, ...] = (
    "Furniture",
    "Beauty & Personal Care",
    "Kitchenware",
    "Sports & Outdoor",
    "Pet Supplies",
    "Shoes",
    "Electronics",
    "Home Supplies",
    "Tools & Hardware",
)


def preset_key(method: str, category: str) -> str:
    slug = category.lower().replace(" & ", "_").replace(" ", "_")
    return f"{method}__{slug}"


def grind_queue() -> list[tuple[str, str]]:
    """(method, category) pairs for launch night diversity."""
    out: list[tuple[str, str]] = []
    for cat in LAUNCH_CATEGORIES:
        for method in ("hardcore", "lurkers", "hundred_gap", "middle_core", "two_hundred"):
            out.append((method, cat))
    return out
