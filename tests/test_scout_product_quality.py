"""Tests for scout product quality gates."""

from __future__ import annotations

from shorts_bot.tiktok_shop.product_scout import ScoutProduct
from shorts_bot.tiktok_shop.scout_product_quality import validate_product
from shorts_bot.tiktok_shop import kalodata_filters


def test_reject_weekly_drop_source() -> None:
    p = ScoutProduct(
        product_id="",
        product_name="Test",
        price=100,
        commission_rate=0.2,
        commission_usd=20,
        gmv_period=50_000,
        creators=50,
        videos=5,
        preset="momentum_weekly_drop",
        score=90,
    )
    q = validate_product(p)
    assert not q.ok
    assert any("weekly" in i.lower() for i in q.issues)


def test_reject_ovios_style_low_commission() -> None:
    p = ScoutProduct(
        product_id="",
        product_name="Ovios Couch",
        price=899,
        commission_rate=0.05,
        commission_usd=44.95,
        gmv_period=230_000,
        creators=160,
        videos=10,
        preset="core_middle_core",
        score=80,
    )
    q = validate_product(p)
    assert not q.ok
    assert any("commission" in i.lower() for i in q.issues)


def test_reject_low_gmv() -> None:
    p = ScoutProduct(
        product_id="",
        product_name="Desk",
        price=120,
        commission_rate=0.15,
        commission_usd=18,
        gmv_period=500,
        creators=40,
        videos=2,
        preset="core_middle_core",
        score=70,
    )
    q = validate_product(p)
    assert not q.ok
    assert any("gmv" in i.lower() for i in q.issues)


def test_pass_coach_pick() -> None:
    p = ScoutProduct(
        product_id="123",
        product_name="Premium Sofa",
        price=450,
        commission_rate=0.12,
        commission_usd=54,
        gmv_period=25_000,
        creators=85,
        videos=12,
        preset="core_middle_core",
        score=85,
    )
    q = validate_product(p)
    assert q.ok


def test_bare_product_url_not_valid_preset() -> None:
    assert kalodata_filters._is_list_filter_url("https://www.kalodata.com/product") is False
    assert kalodata_filters._is_list_filter_url(
        "https://www.kalodata.com/product?region=US&foo=1"
    ) is True
