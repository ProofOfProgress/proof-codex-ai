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
) -> tuple[bool, str, str]:
    """Returns (ok, message, publish_id)."""
    caption = caption.strip()[:2200]
    if account.post_via == "tiktok_api":
        from shorts_bot.tiktok.upload import upload_video

        token_path = account.resolved_token_path()
        if not token_path or not token_path.is_file():
            return False, f"No token at {token_path}", ""
        try:
            result = upload_video(video_path, title=caption, token_path=token_path)
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

    # Default: Zernio with per-account id
    from shorts_bot.zernio.upload import upload_video as zernio_upload

    zid = (account.zernio_account_id or "").strip()
    if not zid:
        return False, f"Account {account.id} needs zernio_account_id in accounts.json", ""
    try:
        # Temporarily override env account — use direct API call
        from shorts_bot.zernio.client import _request, presign_video, upload_file_to_presigned

        upload_url, public_url = presign_video(video_path)
        upload_file_to_presigned(upload_url, video_path)
        payload = {
            "content": caption,
            "mediaItems": [{"type": "video", "url": public_url}],
            "platforms": [{"platform": "tiktok", "accountId": zid}],
            "tiktokSettings": {
                "privacy_level": settings.zernio_tiktok_privacy or "PUBLIC_TO_EVERYONE",
                "allow_comment": True,
                "allow_duet": True,
                "allow_stitch": True,
                "content_preview_confirmed": True,
                "express_consent_given": True,
            },
            "publishNow": True,
        }
        body = _request("POST", "/posts", json=payload)
        post_id = str(body.get("postId") or body.get("_id") or body.get("id") or "")
        log_post(
            account_id=account.id,
            video_path=str(video_path),
            caption=caption,
            product=product,
            ok=True,
            publish_id=post_id,
        )
        return True, f"Zernio posted → {post_id}", post_id
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
