"""Upload Shop clips to the right TikTok account."""

from __future__ import annotations

from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.tiktok_shop.accounts import ShopAccount
from shorts_bot.tiktok_shop.quota import log_post


def post_clip(
    account: ShopAccount,
    *,
    video_path: Path,
    caption: str,
    product: str = "",
    skip_module1_qc: bool = False,
) -> tuple[bool, str, str]:
    """Returns (ok, message, publish_id)."""
    caption = caption.strip()[:2200]

    if account.post_via == "tiktok_api":
        from shorts_bot.tiktok.upload import upload_video

        token_path = account.resolved_token_path()
        if not token_path or not token_path.is_file():
            return False, f"No token at {token_path}", ""
        try:
            result = upload_video(
                video_path,
                title=caption,
                token_path=token_path,
                product=product,
                shop_account_id=account.id,
                skip_pre_publish=skip_module1_qc,
            )
            log_post(
                account_id=account.id,
                video_path=str(video_path),
                caption=caption,
                product=product,
                ok=True,
                publish_id=result.publish_id,
            )
            return True, result.message, result.publish_id
        except Exception as exc:  # noqa: BLE001
            log_post(
                account_id=account.id,
                video_path=str(video_path),
                caption=caption,
                product=product,
                ok=False,
                error=str(exc),
            )
            return False, str(exc), ""

    # Zernio — single upload path (gate runs inside zernio.upload.upload_video)
    from shorts_bot.zernio.upload import upload_video as zernio_upload

    zid = (account.zernio_account_id or "").strip()
    if not zid:
        return False, f"Account {account.id} needs zernio_account_id in accounts.json", ""
    try:
        result = zernio_upload(
            video_path,
            caption=caption,
            tiktok=True,
            facebook=False,
            publish_now=True,
            tiktok_account_id=zid,
            shop_account_id=account.id,
            product=product,
            skip_pre_publish=skip_module1_qc,
        )
        post_id = result.post_id
        log_post(
            account_id=account.id,
            video_path=str(video_path),
            caption=caption,
            product=product,
            ok=True,
            publish_id=post_id,
        )
        return True, result.message, post_id
    except Exception as exc:  # noqa: BLE001
        log_post(
            account_id=account.id,
            video_path=str(video_path),
            caption=caption,
            product=product,
            ok=False,
            error=str(exc),
        )
        return False, str(exc), ""
