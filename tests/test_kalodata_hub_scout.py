"""Tests for Kalodata hub UI scout helpers."""

from __future__ import annotations

import json

from shorts_bot.tiktok_shop import kalodata_filters
from shorts_bot.tiktok_shop.kalodata_hub_scout import extract_products_from_json, _normalize_row
from shorts_bot.tiktok_shop.scout_provider import resolve_scout_provider


def test_extract_products_from_nested_json():
    payload = {
        "data": {
            "list": [
                {
                    "productId": "123",
                    "productName": "Desk Lamp",
                    "price": 89.0,
                    "commissionRate": 12,
                    "revenue": 15000,
                    "creatorCount": 45,
                }
            ]
        }
    }
    rows = extract_products_from_json(payload)
    assert len(rows) == 1
    assert rows[0]["productName"] == "Desk Lamp"


def test_normalize_row_maps_fields():
    norm = _normalize_row(
        {
            "productId": "999",
            "productName": "Mount",
            "price": 29.99,
            "commissionRate": 15,
            "revenue": 12000,
            "creatorCount": 80,
            "videoCount": 12,
        }
    )
    assert norm["product_name"] == "Mount"
    assert norm["spu_avg_price"] == 29.99
    assert norm["total_ifl_cnt"] == 80


def test_preset_has_url(tmp_path, monkeypatch):
    cfg = {
        "presets": {
            "middle_core": {"filter_url": "https://www.kalodata.com/product?x=1"},
            "two_hundred": {"filter_url": ""},
        }
    }
    path = tmp_path / "kalodata_filters.json"
    path.write_text(json.dumps(cfg), encoding="utf-8")
    monkeypatch.setattr(kalodata_filters, "filters_path", lambda: path)
    assert kalodata_filters.preset_has_url("middle_core") is True
    assert kalodata_filters.preset_has_url("two_hundred") is False


def test_auto_prefers_hub_ui_when_url_set(tmp_path, monkeypatch):
    cfg = {"presets": {"middle_core": {"filter_url": "https://www.kalodata.com/product?filters=1"}}}
    path = tmp_path / "kalodata_filters.json"
    path.write_text(json.dumps(cfg), encoding="utf-8")
    monkeypatch.setattr(kalodata_filters, "filters_path", lambda: path)
    fake = type(
        "S",
        (),
        {"scout_provider": "auto", "kalodata_pilot_token": "tok"},
    )()
    monkeypatch.setattr("shorts_bot.tiktok_shop.scout_provider.settings", fake)
    monkeypatch.setattr("shorts_bot.tiktok_shop.scout_provider.kalodata_client.configured", lambda: True)
    assert resolve_scout_provider(preset="middle_core") == "hub_ui"
