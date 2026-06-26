"""Tests for mandatory Module 1 pre-upload QC."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from shorts_bot.tiktok_shop.module1_qc import (
    BANNED_CAPTION_PHRASES,
    _check_caption,
    _check_posting_rules,
    run_module1_qc,
)


def test_banned_caption_phrases_detected():
    hits = _check_caption("Get this Flash Sale before it's gone!")
    assert any("flash sale" in h.lower() for h in hits)


def test_clean_caption_passes():
    assert _check_caption("Love this kitchen gadget for everyday use") == []


def test_duplicate_product_same_day_blocked(tmp_path, monkeypatch):
    log = tmp_path / "tiktok_shop" / "post_log.jsonl"
    log.parent.mkdir(parents=True)
    row = {
        "at": datetime.now(timezone.utc).isoformat(),
        "account_id": "acct_a",
        "product": "Silicone Spatula",
        "ok": True,
    }
    log.write_text(json.dumps(row) + "\n", encoding="utf-8")

    from shorts_bot import config

    monkeypatch.setattr(config.settings, "data_dir", tmp_path)

    violations = _check_posting_rules(account_id="acct_a", product="Silicone Spatula")
    assert any("same product" in v.lower() for v in violations)


def test_post_interval_blocked(tmp_path, monkeypatch):
    log = tmp_path / "tiktok_shop" / "post_log.jsonl"
    log.parent.mkdir(parents=True)
    recent = datetime.now(timezone.utc) - timedelta(minutes=5)
    row = {"at": recent.isoformat(), "account_id": "acct_a", "ok": True}
    log.write_text(json.dumps(row) + "\n", encoding="utf-8")

    from shorts_bot import config

    monkeypatch.setattr(config.settings, "data_dir", tmp_path)
    monkeypatch.setattr(config.settings, "module1_min_post_interval_minutes", 30)

    violations = _check_posting_rules(account_id="acct_a", product="Other")
    assert any("30" in v or "min" in v.lower() for v in violations)


def test_short_video_blocked(tmp_path, monkeypatch):
    from shorts_bot import config

    monkeypatch.setattr(config.settings, "data_dir", tmp_path)
    monkeypatch.setattr(config.settings, "module1_min_video_seconds", 7.0)
    monkeypatch.setattr(config.settings, "module1_qc_blocks_upload", True)
    monkeypatch.setattr(config.settings, "gemini_api_key", None)

    video = tmp_path / "short.mp4"
    report = run_module1_qc(video, caption="ok", product="test")
    assert not report.passed
    assert any("missing" in v.lower() for v in report.violations)


def test_banned_phrases_list_matches_course():
    assert "flash sale" in BANNED_CAPTION_PHRASES
