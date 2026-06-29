"""Bubble wrap — 2-slide photo carousels via Zernio (captions baked into PNGs)."""

from __future__ import annotations

from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.tiktok_shop.accounts import ShopAccount
from shorts_bot.zernio.upload import upload_photo_carousel


def bubble_carousel_defaults(account: ShopAccount) -> dict[str, bool]:
    """Bubble phones finish Mackenzie on device — Zernio sends inbox draft only."""
    if account.track.startswith("bubble"):
        return {"draft": True, "publish_now": False, "auto_add_music": False}
    return {"draft": False, "publish_now": True, "auto_add_music": False}


def post_bubble_wrap_carousel(
    account: ShopAccount,
    *,
    slide1: Path,
    slide2: Path,
    title: str = "Bubble wrap ASMR",
    description: str = "",
    auto_add_music: bool = False,
    publish_now: bool = True,
    draft: bool = False,
    privacy_level: str | None = None,
) -> tuple[bool, str, str]:
    """Upload hook + CTA slides as TikTok photo carousel. Returns (ok, message, post_id)."""
    zid = (account.zernio_account_id or "").strip()
    if not zid:
        return False, f"Account {account.id} needs zernio_account_id in accounts.json", ""

    privacy = privacy_level or settings.zernio_tiktok_privacy or "PUBLIC_TO_EVERYONE"
    if account.track.startswith("bubble"):
        draft = True
        publish_now = False
        auto_add_music = False
    try:
        result = upload_photo_carousel(
            [slide1, slide2],
            title=title,
            description=description,
            tiktok_account_id=zid,
            photo_cover_index=0,
            auto_add_music=auto_add_music,
            publish_now=publish_now,
            draft=draft,
            privacy_level=privacy,
        )
        url = result.platform_urls.get("tiktok", "")
        msg = result.message + (f" → {url}" if url else "")
        return True, msg, result.post_id
    except Exception as exc:  # noqa: BLE001
        return False, str(exc), ""
