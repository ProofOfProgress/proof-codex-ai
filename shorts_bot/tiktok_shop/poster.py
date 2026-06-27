"""Upload Shop clips and bubble-wrap carousels to TikTok accounts."""

from __future__ import annotations

from pathlib import Path

from shorts_bot.tiktok_shop.accounts import ShopAccount
from shorts_bot.tiktok_shop.quota import log_post


def post_clip(
    account: ShopAccount,
    *,
    video_path: Path,
    caption: str,
    product: str = "",
    skip_module1_qc: bool = False,
    private: bool = False,
) -> tuple[bool, str, str]:
    """Returns (ok, message, publish_id). Affiliate MP4 uploads only."""
    caption = caption.strip()[:2200]

    if not skip_module1_qc:
        from shorts_bot.tiktok_shop.module1_qc import enforce_module1_before_upload

        qc = enforce_module1_before_upload(
            video_path,
            caption=caption,
            product=product,
            account_id=account.id,
        )
        if not qc.passed:
            msg = qc.summary()
            log_post(
                account_id=account.id,
                media_path=str(video_path),
                caption=caption,
                product=product,
                ok=False,
                error=msg[:300],
                post_type="video",
            )
            return False, msg, ""

    if account.post_via == "tiktok_api":
        from shorts_bot.tiktok.upload import upload_video

        token_path = account.resolved_token_path()
        if not token_path or not token_path.is_file():
            return False, f"No token at {token_path}", ""
        try:
            result = upload_video(video_path, title=caption, token_path=token_path)
            log_post(
                account_id=account.id,
                media_path=str(video_path),
                caption=caption,
                product=product,
                ok=True,
                publish_id=result.publish_id,
                post_type="video",
            )
            return True, result.message, result.publish_id
        except Exception as exc:  # noqa: BLE001
            log_post(
                account_id=account.id,
                media_path=str(video_path),
                caption=caption,
                product=product,
                ok=False,
                error=str(exc),
                post_type="video",
            )
            return False, str(exc), ""

    zid = (account.zernio_account_id or "").strip()
    if not zid:
        return False, f"Account {account.id} needs zernio_account_id in accounts.json", ""

    from shorts_bot.zernio.upload import upload_video as zernio_upload

    try:
        result = zernio_upload(
            video_path,
            caption=caption,
            tiktok=True,
            facebook=False,
            private=private,
            tiktok_account_id=zid,
        )
        log_post(
            account_id=account.id,
            media_path=str(video_path),
            caption=caption,
            product=product,
            ok=True,
            publish_id=result.post_id,
            post_type="video",
        )
        return True, result.message, result.post_id
    except Exception as exc:  # noqa: BLE001
        log_post(
            account_id=account.id,
            media_path=str(video_path),
            caption=caption,
            product=product,
            ok=False,
            error=str(exc),
            post_type="video",
        )
        return False, str(exc), ""


def post_carousel(
    account: ShopAccount,
    *,
    slide1: Path,
    slide2: Path,
    title: str,
    caption: str = "",
    private: bool = False,
) -> tuple[bool, str, str]:
    """Post a 2-image bubble-wrap slideshow. No Module 1 QC (not affiliate video)."""
    from shorts_bot.tiktok_shop.bubble_wrap import validate_slides

    errors = validate_slides(slide1, slide2)
    if errors:
        msg = "; ".join(errors)
        log_post(
            account_id=account.id,
            media_path=f"{slide1}|{slide2}",
            caption=caption or title,
            ok=False,
            error=msg[:300],
            post_type="carousel",
        )
        return False, msg, ""

    zid = (account.zernio_account_id or "").strip()
    if account.post_via != "zernio":
        return False, "Photo carousels require post_via=zernio", ""
    if not zid:
        return False, f"Account {account.id} needs zernio_account_id in accounts.json", ""

    from shorts_bot.zernio.upload import upload_photo_carousel

    try:
        result = upload_photo_carousel(
            [slide1, slide2],
            title=title,
            caption=caption,
            tiktok_account_id=zid,
            private=private,
        )
        log_post(
            account_id=account.id,
            media_path=f"{slide1}|{slide2}",
            caption=caption or title,
            ok=True,
            publish_id=result.post_id,
            post_type="carousel",
        )
        return True, result.message, result.post_id
    except Exception as exc:  # noqa: BLE001
        log_post(
            account_id=account.id,
            media_path=f"{slide1}|{slide2}",
            caption=caption or title,
            ok=False,
            error=str(exc),
            post_type="carousel",
        )
        return False, str(exc), ""
