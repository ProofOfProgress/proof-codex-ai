"""Affiliate Shop videos — Zernio inbox draft + phone hub product link finish.

TikTok / Zernio cannot attach the orange shopping cart via API. Affiliate accounts
with a dedicated hub phone (phone_5) upload MP4 to inbox; the phone finishes
Add Link → Products → publish.
"""

from __future__ import annotations

from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.tiktok_shop.accounts import ShopAccount
from shorts_bot.zernio.upload import upload_video


def affiliate_video_defaults(account: ShopAccount) -> dict[str, bool]:
    """Affiliate with hub phone → inbox draft only until product link is added on device."""
    if account.track.startswith("affiliate") and (account.phone_hub_slot or "").strip():
        return {"draft": True, "publish_now": False}
    return {"draft": False, "publish_now": True}


def needs_phone_product_finish(account: ShopAccount) -> bool:
    return affiliate_video_defaults(account)["draft"]


def post_affiliate_video(
    account: ShopAccount,
    *,
    video_path: Path,
    caption: str,
    product_id: str = "",
    product_name: str = "",
    publish_now: bool | None = None,
    draft: bool | None = None,
) -> tuple[bool, str, str]:
    """Upload affiliate MP4 via Zernio. Returns (ok, message, post_id)."""
    zid = (account.zernio_account_id or "").strip()
    if not zid:
        return False, f"Account {account.id} needs zernio_account_id in accounts.json", ""

    defaults = affiliate_video_defaults(account)
    if draft is None:
        draft = defaults["draft"]
    if publish_now is None:
        publish_now = defaults["publish_now"]

    try:
        result = upload_video(
            video_path,
            caption=caption,
            tiktok=True,
            facebook=False,
            tiktok_account_id=zid,
            draft=draft,
            publish_now=publish_now and not draft,
        )
        extra = ""
        if product_id or product_name:
            extra = f" product={product_name or product_id}"
        if draft:
            msg = f"Zernio inbox draft{extra} — finish product link on {account.phone_hub_slot or 'phone'}"
        else:
            msg = result.message + extra
        return True, msg, result.post_id
    except Exception as exc:  # noqa: BLE001
        return False, str(exc), ""
