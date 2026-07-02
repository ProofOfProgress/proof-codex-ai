"""Tests for Kalodata KaloPilot scout."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from shorts_bot.tiktok_shop import kalodata_client
from shorts_bot.tiktok_shop import kalodata_filters
from shorts_bot.tiktok_shop.kalodata_scout import _parse_table_rows, _scout_query, scout_via_kalodata
from shorts_bot.tiktok_shop.scout_provider import resolve_scout_provider


def test_kalodata_configured(monkeypatch):
    fake = type("S", (), {"kalodata_pilot_token": ""})()
    monkeypatch.setattr("shorts_bot.tiktok_shop.kalodata_client.settings", fake)
    assert kalodata_client.configured() is False

    fake = type("S", (), {"kalodata_pilot_token": "abc123def"})()
    monkeypatch.setattr("shorts_bot.tiktok_shop.kalodata_client.settings", fake)
    assert kalodata_client.configured() is True


def test_parse_table_rows():
    text = """
| product_name | product_id | price_usd | commission_pct | gmv_usd | creators | videos | trend | cover_url |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Phone Mount | 12345 | 29.99 | 15 | 12000 | 80 | 12 | up | https://x/img.jpg |
"""
    rows = _parse_table_rows(text)
    assert len(rows) == 1
    assert rows[0]["product_name"] == "Phone Mount"
    assert rows[0]["product_id"] == "12345"


def test_scout_query_includes_coach_filters():
    q = _scout_query(preset="middle_core", limit=8)
    assert "10,000" in q or "10000" in q
    assert "200" in q
    assert "8%" in q


def test_resolve_scout_provider_prefers_kalodata(monkeypatch, tmp_path):
    cfg = {"presets": {"middle_core": {"filter_url": ""}}}
    path = tmp_path / "kalodata_filters.json"
    path.write_text(json.dumps({"presets": {}}), encoding="utf-8")
    monkeypatch.setattr(kalodata_filters, "filters_path", lambda: path)
    fake = type(
        "S",
        (),
        {
            "scout_provider": "auto",
            "kalodata_pilot_token": "tok",
            "fastmoss_client_id": "id",
            "fastmoss_client_secret": "sec",
        },
    )()
    monkeypatch.setattr("shorts_bot.tiktok_shop.scout_provider.settings", fake)
    monkeypatch.setattr("shorts_bot.tiktok_shop.scout_provider.kalodata_client.configured", lambda: True)
    monkeypatch.setattr("shorts_bot.tiktok_shop.scout_provider.fastmoss_client.configured", lambda: True)
    assert resolve_scout_provider(preset="middle_core") == "kalodata"


def test_scout_via_kalodata_parses_table(monkeypatch):
    monkeypatch.setattr("shorts_bot.tiktok_shop.kalodata_scout.kalodata_client.configured", lambda: True)
    monkeypatch.setattr(
        "shorts_bot.tiktok_shop.kalodata_scout.kalodata_client.query_and_wait",
        lambda query, **kwargs: {
            "status": "completed",
            "text": (
                "| product_name | product_id | price_usd | commission_pct | gmv_usd | creators | videos | trend | cover_url |\n"
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
                "| Desk Lamp | 999 | 89.00 | 12 | 15000 | 45 | 8 | rising | |\n"
            ),
        },
    )
    fake_settings = type("S", (), {"kalodata_region": "US", "gemini_api_key": ""})()
    monkeypatch.setattr("shorts_bot.tiktok_shop.kalodata_scout.settings", fake_settings)

    products = scout_via_kalodata(preset="middle_core", limit=5)
    assert len(products) == 1
    assert products[0].product_name == "Desk Lamp"
    assert products[0].gmv_period == 15000


def test_resolve_scout_provider_momentum_fallback(monkeypatch, tmp_path):
    import json

    weekly = tmp_path / "tiktok_shop" / "momentum_weekly_drop.json"
    weekly.parent.mkdir(parents=True)
    weekly.write_text(json.dumps({"products": [{"product_name": "Test Kit"}]}), encoding="utf-8")

    filters = tmp_path / "kalodata_filters.json"
    filters.write_text(json.dumps({"presets": {}}), encoding="utf-8")
    monkeypatch.setattr(kalodata_filters, "filters_path", lambda: filters)

    fake = type("S", (), {"scout_provider": "auto", "data_dir": tmp_path})()
    monkeypatch.setattr("shorts_bot.tiktok_shop.scout_provider.settings", fake)
    monkeypatch.setattr("shorts_bot.tiktok_shop.scout_provider.kalodata_client.configured", lambda: False)
    monkeypatch.setattr("shorts_bot.tiktok_shop.scout_provider.fastmoss_client.configured", lambda: False)
    assert resolve_scout_provider(preset="middle_core") == "momentum_weekly_drop"
