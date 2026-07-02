"""Tests for KaloPilot query builder and scout provider priority."""

from __future__ import annotations

from shorts_bot.tiktok_shop.kalodata_pilot_queries import build_pilot_query, normalize_method
from shorts_bot.tiktok_shop.scout_provider import resolve_scout_provider


def test_normalize_method_aliases() -> None:
    assert normalize_method("core_middle_core") == "middle_core"
    assert normalize_method("sauce_hardcore") == "hardcore"


def test_build_pilot_query_includes_course_filters() -> None:
    q = build_pilot_query(preset="middle_core", category="Furniture", limit=5)
    assert "middle_core" in q.lower() or "middle core" in q.lower()
    assert "Furniture" in q
    assert "50" in q  # growth min
    assert "commission" in q.lower()


def test_auto_prefers_kalodata_when_token_set(tmp_path, monkeypatch) -> None:
    from shorts_bot.tiktok_shop import kalodata_filters

    cfg = {"presets": {"core_middle_core": {"filter_url": "https://www.kalodata.com/product?x=1"}}}
    path = tmp_path / "kalodata_filters.json"
    path.write_text(__import__("json").dumps(cfg), encoding="utf-8")
    monkeypatch.setattr(kalodata_filters, "filters_path", lambda: path)
    fake = type("S", (), {"scout_provider": "auto", "kalodata_pilot_token": "tok"})()
    monkeypatch.setattr("shorts_bot.tiktok_shop.scout_provider.settings", fake)
    monkeypatch.setattr("shorts_bot.tiktok_shop.scout_provider.kalodata_client.configured", lambda: True)
    assert resolve_scout_provider(preset="middle_core") == "kalodata"
