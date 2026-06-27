# Tests for bubble wrap + accounts wiring

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from shorts_bot.tiktok_shop.accounts import ShopAccount, load_accounts, total_daily_cap
from shorts_bot.tiktok_shop.accounts_cli import scaffold_accounts, validate_accounts
from shorts_bot.tiktok_shop.bubble_wrap import default_caption, validate_slides
from shorts_bot.tiktok_shop.captions import caption_variants, sanitize_caption
from shorts_bot.tiktok_shop.poster import post_carousel
from shorts_bot.tiktok_shop.queue import enqueue_carousel, pending_posts
from shorts_bot.tiktok_shop.quota import remaining_today


def test_three_accounts_thirty_cap():
    accts = [
        ShopAccount(id=f"shop_{i}", label=f"S{i}", daily_limit=10)
        for i in range(1, 4)
    ]
    assert total_daily_cap(accts) == 30
    assert remaining_today(accts[0]) == 10


def test_captions_no_percent():
    caps = caption_variants("Car mount", limit=3)
    assert caps
    for cap in caps:
        assert "%" not in cap
    bad = sanitize_caption("50% off today only")
    assert "50" not in bad or "%" not in bad


def test_sanitize_strips_percent_off():
    assert "%" not in sanitize_caption("Get 30% off now")


def test_validate_slides(tmp_path: Path):
    s1 = tmp_path / "a.png"
    s2 = tmp_path / "b.png"
    s1.write_bytes(b"x")
    s2.write_bytes(b"y")
    assert validate_slides(s1, s2) == []


def test_validate_slides_same_file_fails(tmp_path: Path):
    s = tmp_path / "a.png"
    s.write_bytes(b"x")
    assert any("different" in e for e in validate_slides(s, s))


def test_scaffold_and_validate_accounts(tmp_path: Path, monkeypatch):
    cfg = tmp_path / "accounts.json"
    monkeypatch.setattr(
        "shorts_bot.tiktok_shop.accounts.accounts_config_path",
        lambda: cfg,
    )

    path = scaffold_accounts(track="bubble", count=2)
    assert path == cfg
    assert cfg.is_file()
    issues = validate_accounts()
    assert len(issues) == 2
    assert all("zernio_account_id" in i for i in issues)


def test_load_accounts_with_zernio(tmp_path: Path, monkeypatch):
    cfg = tmp_path / "accounts.json"
    cfg.write_text(
        """{
  "accounts": [{
    "id": "bubble_1",
    "label": "Test",
    "track": "bubble",
    "post_via": "zernio",
    "zernio_account_id": "abc123"
  }]
}""",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "shorts_bot.tiktok_shop.accounts.accounts_config_path",
        lambda: cfg,
    )
    accts = load_accounts()
    assert accts[0].zernio_account_id == "abc123"
    assert accts[0].track == "bubble"


def test_enqueue_carousel(tmp_path: Path, monkeypatch):
    q = tmp_path / "queue.json"
    monkeypatch.setattr("shorts_bot.tiktok_shop.queue.queue_path", lambda: q)
    enqueue_carousel(slide1_path="a.png", slide2_path="b.png", title="Hook", caption="#fyp")
    pending = pending_posts(media_type="carousel")
    assert len(pending) == 1
    assert pending[0]["title"] == "Hook"


def test_post_carousel_success(tmp_path: Path):
    s1 = tmp_path / "1.png"
    s2 = tmp_path / "2.png"
    s1.write_bytes(b"a")
    s2.write_bytes(b"b")
    acct = ShopAccount(id="b1", label="B", zernio_account_id="zid", track="bubble")

    fake = MagicMock()
    fake.post_id = "p1"
    fake.message = "ok"

    with patch("shorts_bot.zernio.upload.upload_photo_carousel", return_value=fake):
        ok, msg, pub = post_carousel(
            acct,
            slide1=s1,
            slide2=s2,
            title="Hook",
            caption=default_caption(),
            private=True,
        )
    assert ok
    assert pub == "p1"


def test_post_carousel_missing_zernio_id(tmp_path: Path):
    s1 = tmp_path / "1.png"
    s2 = tmp_path / "2.png"
    s1.write_bytes(b"a")
    s2.write_bytes(b"b")
    acct = ShopAccount(id="b1", label="B", track="bubble")
    ok, msg, _ = post_carousel(acct, slide1=s1, slide2=s2, title="Hook")
    assert not ok
    assert "zernio_account_id" in msg
