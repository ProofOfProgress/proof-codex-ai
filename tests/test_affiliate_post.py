"""Affiliate inbox draft + phone hub finish tests."""

from __future__ import annotations

from shorts_bot.tiktok_shop.accounts import ShopAccount
from shorts_bot.tiktok_shop.affiliate_post import affiliate_video_defaults, needs_phone_product_finish


def test_affiliate_with_phone_5_inbox_draft():
    acct = ShopAccount(
        id="affiliate_main",
        label="main",
        track="affiliate",
        phone_hub_slot="phone_5",
    )
    assert affiliate_video_defaults(acct) == {"draft": True, "publish_now": False}
    assert needs_phone_product_finish(acct) is True


def test_affiliate_without_phone_live_publish():
    acct = ShopAccount(
        id="affiliate_test",
        label="test",
        track="affiliate",
        phone_hub_slot="",
    )
    assert affiliate_video_defaults(acct) == {"draft": False, "publish_now": True}
    assert needs_phone_product_finish(acct) is False
