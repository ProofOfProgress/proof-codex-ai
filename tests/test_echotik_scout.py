# Tests for EchoTik product scout

from pathlib import Path
from unittest.mock import patch

from shorts_bot.tiktok_shop import echotik_client
from shorts_bot.tiktok_shop.product_scout import (
    _score_middle_core,
    _score_two_hundred,
    load_products,
    save_products,
    scout_products,
)


def test_echotik_configured(monkeypatch):
    def _patch(user: str, password: str) -> None:
        fake = type("S", (), {
            "echotik_username": user,
            "echotik_password": password,
        })()
        monkeypatch.setattr("shorts_bot.tiktok_shop.echotik_client.settings", fake)

    _patch("", "")
    assert echotik_client.configured() is False

    _patch("your-username", "secret")
    assert echotik_client.configured() is False

    _patch("api_user", "api_pass")
    assert echotik_client.configured() is True


def test_middle_core_scores_high_gmv_product():
    row = {
        "spu_avg_price": 35,
        "product_commission_rate": 25,
        "total_sale_gmv_amt": 15000,
        "total_ifl_cnt": 80,
        "total_video_cnt": 12,
    }
    score, issues = _score_middle_core(row)
    assert score >= 50
    assert issues == []


def test_two_hundred_rejects_many_creators():
    row = {
        "spu_avg_price": 25,
        "product_commission_rate": 20,
        "total_sale_gmv_1d_amt": 12000,
        "total_ifl_cnt": 300,
        "total_video_cnt": 5,
    }
    score, issues = _score_two_hundred(row)
    assert any("creators" in issue for issue in issues)
    assert score < 100


def test_scout_products_filters_and_saves(tmp_path: Path, monkeypatch):
    fake_settings = type("S", (), {
        "data_dir": tmp_path,
        "echotik_region": "US",
    })()
    monkeypatch.setattr("shorts_bot.config.settings", fake_settings)
    monkeypatch.setattr("shorts_bot.tiktok_shop.product_scout.settings", fake_settings)

    good = {
        "product_id": "111",
        "product_name": "Car phone mount",
        "spu_avg_price": 35,
        "product_commission_rate": 25,
        "total_sale_gmv_amt": 15000,
        "total_ifl_cnt": 80,
        "total_video_cnt": 12,
        "cover_url": "https://example.com/cover.jpg",
    }
    bad = {
        "product_id": "222",
        "product_name": "Low GMV item",
        "spu_avg_price": 5,
        "product_commission_rate": 5,
        "total_sale_gmv_amt": 100,
        "total_ifl_cnt": 500,
        "total_video_cnt": 0,
    }

    with patch(
        "shorts_bot.tiktok_shop.product_scout.fetch_rank_rows",
        return_value=[good, bad],
    ), patch(
        "shorts_bot.tiktok_shop.product_scout.echotik_client.product_detail",
        return_value=[good],
    ):
        products = scout_products(preset="middle_core", limit=5)

    assert len(products) == 1
    assert products[0].product_id == "111"
    assert products[0].commission_usd >= 5

    path = save_products(products)
    assert path.is_file()
    loaded = load_products()
    assert loaded[0]["product_name"] == "Car phone mount"
    assert loaded[0]["cover_url"] == "https://example.com/cover.jpg"
