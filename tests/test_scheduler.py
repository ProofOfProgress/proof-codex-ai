"""Affiliate scheduler — cron tick without Cursor automations."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

from shorts_bot.tiktok_shop.scheduler import (
    min_post_interval_seconds,
    seconds_until_next_post,
    tick_post,
)


def test_min_post_interval_default_30_minutes(monkeypatch):
    class FakeSettings:
        tiktok_shop_min_post_interval_minutes = 30

    monkeypatch.setattr("shorts_bot.tiktok_shop.scheduler.settings", FakeSettings())
    assert min_post_interval_seconds() == 1800


def test_seconds_until_next_post_after_recent(tmp_path, monkeypatch):
    class FakeSettings:
        data_dir = tmp_path
        tiktok_shop_min_post_interval_minutes = 30

    monkeypatch.setattr("shorts_bot.tiktok_shop.scheduler.settings", FakeSettings())
    log = tmp_path / "tiktok_shop" / "post_log.jsonl"
    log.parent.mkdir(parents=True)
    recent = datetime.now(timezone.utc).isoformat()
    log.write_text(
        json.dumps(
            {
                "at": recent,
                "account_id": "affiliate_main",
                "ok": True,
                "video": "x.mp4",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    wait = seconds_until_next_post("affiliate_main")
    assert 1700 <= wait <= 1800


def test_tick_skips_disabled_account(monkeypatch):
    from shorts_bot.tiktok_shop.accounts import ShopAccount

    monkeypatch.setattr(
        "shorts_bot.tiktok_shop.scheduler.load_account",
        lambda _id: ShopAccount(
                id="affiliate_main",
                label="Test",
                track="affiliate",
                daily_limit=10,
                enabled=False,
                post_via="zernio",
                zernio_account_id="x",
            ),
    )
    result = tick_post(account_id="affiliate_main", confirm=True)
    assert result.action == "skipped"
    assert "disabled" in result.message.lower()
