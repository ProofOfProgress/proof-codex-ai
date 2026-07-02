"""Tests for Kalodata filter verification gates."""

from __future__ import annotations

from shorts_bot.tiktok_shop.kalodata_filter_spec import build_spec
from shorts_bot.tiktok_shop.kalodata_filter_verify import (
    ParsedKalodataUi,
    safe_click,
    verify_before_submit,
)


def test_refuse_clicks_outside_sidebar() -> None:
    try:
        safe_click(900, 500)
        raised = False
    except ValueError as exc:
        raised = True
        assert "misclick" in str(exc).lower()
    assert raised


def test_reject_product_detail_page() -> None:
    spec = build_spec(method="middle_core", category="Furniture")
    ui = ParsedKalodataUi(
        page_type="product_detail",
        date_range="last 30 days",
        revenue_growth_min_pct=0,
        category="Furniture",
    )
    res = verify_before_submit(spec, ui)
    assert not res.ok
    assert any("WRONG PAGE" in i for i in res.issues)


def test_reject_last_30_when_middle_core() -> None:
    spec = build_spec(method="middle_core", category="Furniture")
    ui = ParsedKalodataUi(
        page_type="product_list",
        date_range="last 30 days",
        revenue_growth_min_pct=0,
        category="Furniture",
    )
    res = verify_before_submit(spec, ui)
    assert not res.ok
    assert any("30" in i for i in res.issues)


def test_pass_middle_core_furniture() -> None:
    spec = build_spec(method="middle_core", category="Furniture")
    ui = ParsedKalodataUi(
        page_type="product_list",
        date_range="last 7 days",
        category="Furniture",
        revenue_growth_min_pct=50,
        creator_max=200,
        commission_min_pct=20,
        avg_unit_price_min=80,
        filtering_pills=["Dates: Last 7 Days", "Category: Furniture"],
        submit_enabled=True,
    )
    res = verify_before_submit(spec, ui)
    assert res.ok


def test_coach_overlay_raises_commission_floor() -> None:
    spec = build_spec(method="two_hundred", category="Furniture")
    assert spec.commission_min_pct >= 8
    assert spec.avg_unit_price_min >= 80
