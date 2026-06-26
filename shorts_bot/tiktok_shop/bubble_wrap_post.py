"""Bubble wrap — 2-slide photo carousels via Zernio (captions baked into PNGs)."""

from __future__ import annotations

from pathlib import Path

from shorts_bot.tiktok_shop.accounts import ShopAccount
from shorts_bot.zernio.upload import upload_photo_carousel


def post_bubble_wrap_carousel(
    account: ShopAccount,
    *,
    slide1: Path,
    slide2: Path,
    title: str = "Bubble wrap ASMR",
    description: str = "",
    auto_add_music: bool = False,
    publish_now: bool = True,
) -> tuple[bool, str, str]:
    """Upload hook + CTA PNGs as TikTok photo carousel. Returns (ok, message, post_id)."""
    zid = (account.zernio_account_id or "").strip()
    if not zid:
        return False, f"Account {account.id} needs zernio_account_id in accounts.json", ""

    try:
        result = upload_photo_carousel(
            [slide1, slide2],
            title=title,
            description=description,
            tiktok_account_id=zid,
            photo_cover_index=0,
            auto_add_music=auto_add_music,
            publish_now=publish_now,
        )
        return True, result.message, result.post_id
    except Exception as exc:  # noqa: BLE001
        return False, str(exc), ""

