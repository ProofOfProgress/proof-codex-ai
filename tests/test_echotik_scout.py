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


def test_scout_products_raises_without_backend():
    with patch("shorts_bot.tiktok_shop.scout_provider.resolve_scout_provider", return_value=""):
        try:
            scout_products(preset="middle_core", limit=5)
        except RuntimeError as exc:
            msg = str(exc)
            assert "KALODATA" in msg or "kalodata" in msg.lower() or "Filter URLs" in msg
        else:
            raise AssertionError("expected RuntimeError")


def test_scout_products_fastmoss_stub_raises_when_configured():
    with patch("shorts_bot.tiktok_shop.scout_provider.resolve_scout_provider", return_value="fastmoss"), patch(
        "shorts_bot.tiktok_shop.fastmoss_client.ping",
        return_value={"message": "FastMoss scout not wired yet"},
    ):
        try:
            scout_products(preset="middle_core", limit=5)
        except RuntimeError as exc:
            assert "not wired" in str(exc).lower()
        else:
            raise AssertionError("expected RuntimeError")


def test_fetch_daily_rank_rows_walks_back(monkeypatch):
    from datetime import date as real_date

    calls: list[str] = []

    class FakeDate(real_date):
        @classmethod
        def today(cls):
            return real_date(2026, 6, 28)

    monkeypatch.setattr("shorts_bot.tiktok_shop.product_scout.date", FakeDate)

    def fake_ranklist(*, date: str, **kwargs):
        calls.append(date)
        if date == "2026-06-26":
            return [{"product_id": "1", "product_name": "Hit"}]
        return []

    monkeypatch.setattr("shorts_bot.tiktok_shop.product_scout.echotik_client.product_ranklist", fake_ranklist)
    from shorts_bot.tiktok_shop.product_scout import _fetch_daily_rank_rows

    rows = _fetch_daily_rank_rows(pages=1, start_days_back=1, max_days_back=5)
    assert len(rows) == 1
    assert calls[0] == "2026-06-27"
    assert "2026-06-26" in calls


def test_echotik_ping_quota_error(monkeypatch):
    def fake_ranklist(**kwargs):
        raise RuntimeError("EchoTik error: Usage Limit Exceeded, Please Contact Administrator")

    monkeypatch.setattr("shorts_bot.tiktok_shop.echotik_client.product_ranklist", fake_ranklist)
    result = echotik_client.ping(max_days_back=1)
    assert result["ok"] is False
    assert result["error"] == "quota_exceeded"
