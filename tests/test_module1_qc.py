"""Tests for mandatory Module 1 pre-upload QC."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from shorts_bot.tiktok_shop.captions import (
    ON_SCREEN_CAPTION_TEMPLATE,
    caption_variants,
    on_screen_caption,
)
from shorts_bot.tiktok_shop.module1_qc import (
    BANNED_CAPTION_PHRASES,
    MODULE7_BANNED_CAPTION_WORDS,
    Module1QCReport,
    _check_aspect_ratio,
    _check_caption,
    _check_posting_rules,
    run_module1_qc,
    run_module1_qc_batch,
)
from shorts_bot.tiktok_shop.queue import enqueue_video


def test_banned_caption_phrases_detected():
    hits = _check_caption("Get this Flash Sale before it's gone!")
    assert any("flash sale" in h.lower() for h in hits)


def test_module7_words_blocked():
    for word in ("sale", "price", "discount", "coupon"):
        hits = _check_caption(f"This {word} is amazing today")
        assert any(word in h.lower() for h in hits), f"Expected block for {word}"


def test_free_shipping_blocked():
    hits = _check_caption("Grab it with free shipping today")
    assert hits


def test_clean_caption_passes():
    assert _check_caption("Love this kitchen gadget for everyday use") == []


def test_on_screen_caption_has_no_module7_words():
    cap = on_screen_caption("Insulated Tumbler")
    lower = cap.lower()
    for word in MODULE7_BANNED_CAPTION_WORDS:
        assert word not in lower.split(), f"Default hook contains {word}"


def test_caption_variants_avoid_module7_words():
    for cap in caption_variants("Silicone Spatula", limit=10):
        lower = cap.lower()
        for word in MODULE7_BANNED_CAPTION_WORDS:
            assert word not in lower, f"Variant contains {word}: {cap}"


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


def test_module1_includes_brand_and_phone_rules():
    from shorts_bot.tiktok_shop.module1_qc import MODULE1_VIDEO_VIOLATIONS

    joined = " ".join(MODULE1_VIDEO_VIOLATIONS).lower()
    assert "phone screens" in joined
    assert "third-party brands" in joined
    assert "app icons" in joined


def test_aspect_ratio_blocks_landscape():
    hits = _check_aspect_ratio(1920, 1080)
    assert any("9:16" in h for h in hits)


def test_aspect_ratio_allows_vertical():
    assert _check_aspect_ratio(1080, 1920) == []


def test_enqueue_blocks_when_qc_fails(tmp_path, monkeypatch):
    from shorts_bot import config

    monkeypatch.setattr(config.settings, "data_dir", tmp_path)
    monkeypatch.setattr(config.settings, "module1_require_qc_before_enqueue", True)

    video = tmp_path / "clip.mp4"
    video.write_bytes(b"x")

    fail_report = Module1QCReport(passed=False, violations=["test violation"])

    monkeypatch.setattr(
        "shorts_bot.tiktok_shop.module1_qc.run_module1_qc",
        lambda *a, **k: fail_report,
    )

    with pytest.raises(RuntimeError, match="Module 1 QC BLOCKED"):
        enqueue_video(
            video_path=str(video),
            product="Test Product",
            caption="clean caption here",
        )


def test_enqueue_succeeds_when_qc_passes(tmp_path, monkeypatch):
    from shorts_bot import config

    monkeypatch.setattr(config.settings, "data_dir", tmp_path)
    monkeypatch.setattr(config.settings, "module1_require_qc_before_enqueue", True)

    video = tmp_path / "clip.mp4"
    video.write_bytes(b"x")

    pass_report = Module1QCReport(passed=True)

    monkeypatch.setattr(
        "shorts_bot.tiktok_shop.module1_qc.run_module1_qc",
        lambda *a, **k: pass_report,
    )

    idx = enqueue_video(
        video_path=str(video),
        product="Test Product",
        caption="clean caption here",
    )
    assert idx == 0
    rows = json.loads((tmp_path / "tiktok_shop" / "queue.json").read_text())
    assert rows[0]["qc_passed"] is True


def test_qc_batch_counts(tmp_path, monkeypatch):
    from shorts_bot import config

    monkeypatch.setattr(config.settings, "data_dir", tmp_path)
    monkeypatch.setattr(config.settings, "module1_qc_enabled", True)

    v1 = tmp_path / "a.mp4"
    v2 = tmp_path / "b.mp4"
    v1.write_bytes(b"a")
    v2.write_bytes(b"b")

    def fake_qc(path, **kwargs):
        if path.name == "a.mp4":
            return Module1QCReport(passed=True)
        return Module1QCReport(passed=False, violations=["blocked"])

    monkeypatch.setattr("shorts_bot.tiktok_shop.module1_qc.run_module1_qc", fake_qc)

    batch = run_module1_qc_batch(
        [(v1, "ok", "prod"), (v2, "ok", "prod")],
        account_id="affiliate_main",
    )
    assert batch.total == 2
    assert batch.passed == 1
    assert batch.failed == 1
