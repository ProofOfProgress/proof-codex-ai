"""Tests for Kalodata grind matrix (method × category queue)."""

from shorts_bot.tiktok_shop.kalodata_grind_matrix import (
    COACH_OVERLAY,
    LAUNCH_CATEGORIES,
    METHODS,
    grind_queue,
    preset_key,
)


def test_grind_queue_covers_methods_and_categories():
    q = grind_queue()
    assert len(q) == len(LAUNCH_CATEGORIES) * len(METHODS)
    assert ("middle_core", "Furniture") in q


def test_preset_key_slug():
    assert preset_key("hardcore", "Beauty & Personal Care") == "hardcore__beauty_personal_care"


def test_coach_overlay_matches_launch_bar():
    assert COACH_OVERLAY["commission_min_pct"] >= 8
    assert COACH_OVERLAY["avg_unit_price_min"] >= 80
