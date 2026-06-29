# Tests for TikTok Shop factory

from pathlib import Path

from shorts_bot.tiktok_shop.accounts import ShopAccount, total_daily_cap
from shorts_bot.tiktok_shop.captions import caption_variants, sanitize_caption
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


def test_on_screen_caption_template():
    from shorts_bot.tiktok_shop.captions import format_product_title, on_screen_caption

    assert format_product_title("pre workout powder") == "Pre Workout Powder"
    cap = on_screen_caption("pre workout powder")
    assert "SO sorry" in cap
    assert "this pre workout powder" in cap
    assert "selling out on Shop" in cap
    assert "discount" not in cap.lower()
