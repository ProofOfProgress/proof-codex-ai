"""Upload MP4 to TikTok + Facebook via Zernio."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from shorts_bot.config import settings
from shorts_bot.zernio.client import (
    _request,
    account_id_for,
    credentials_configured,
    presign_media,
    presign_video,
    upload_file_to_presigned,
)


@dataclass
class ZernioPostResult:
    post_id: str
    status: str
    message: str
    platform_urls: dict[str, str] = field(default_factory=dict)


def _platform_targets(*, tiktok: bool = True, facebook: bool = True) -> list[dict[str, Any]]:
    platforms: list[dict[str, Any]] = []
    if tiktok and settings.zernio_post_tiktok:
        tid = account_id_for("tiktok")
        if not tid:
            raise RuntimeError("No TikTok account on Zernio — connect in zernio.com dashboard")
        platforms.append({"platform": "tiktok", "accountId": tid})
    if facebook and settings.zernio_post_facebook:
        fid = account_id_for("facebook")
        if not fid:
            raise RuntimeError("No Facebook account on Zernio — connect in zernio.com dashboard")
        platforms.append(
            {
                "platform": "facebook",
                "accountId": fid,
                "platformSpecificData": {
                    "contentType": "reel",
                    "title": settings.zernio_facebook_reel_title or "TikTok Shop",
                },
            }
        )
    if not platforms:
        raise RuntimeError("No Zernio platforms enabled (ZERNIO_POST_TIKTOK / ZERNIO_POST_FACEBOOK)")
    return platforms


def _tiktok_platform_entry(*, account_id: str | None = None) -> dict[str, Any]:
    zid = (account_id or account_id_for("tiktok") or "").strip()
    if not zid:
        raise RuntimeError("No TikTok account on Zernio — connect in zernio.com dashboard")
    return {"platform": "tiktok", "accountId": zid}


def upload_photo_carousel(
    image_paths: list[Path],
    *,
    title: str = "",
    description: str = "",
    tiktok_account_id: str | None = None,
    photo_cover_index: int = 0,
    auto_add_music: bool = False,
    publish_now: bool = True,
    draft: bool = False,
    privacy_level: str | None = None,
) -> ZernioPostResult:
    """Post a TikTok photo carousel (2+ images) — bubble wrap slideshow format."""
    if not credentials_configured():
        raise RuntimeError("ZERNIO_API_KEY not configured")
    paths = [Path(p) for p in image_paths]
    if len(paths) < 2:
        raise ValueError("Photo carousel requires at least 2 images")
    for p in paths:
        if not p.is_file():
            raise FileNotFoundError(p)

    media_items: list[dict[str, str]] = []
    for p in paths:
        upload_url, public_url = presign_media(p)
        upload_file_to_presigned(upload_url, p)
        media_items.append({"type": "image", "url": public_url})

    privacy = (privacy_level or settings.zernio_tiktok_privacy or "PUBLIC_TO_EVERYONE").strip()
    tiktok_settings: dict[str, Any] = {
        "privacy_level": privacy,
        "allow_comment": True,
        "media_type": "photo",
        "photo_cover_index": max(0, photo_cover_index),
        "content_preview_confirmed": True,
        "express_consent_given": True,
        "auto_add_music": auto_add_music,
    }
    desc_clean = (description or "").strip()[:4000]
    if desc_clean:
        tiktok_settings["description"] = desc_clean
    if draft:
        tiktok_settings["draft"] = True
    if settings.zernio_declare_aigc:
        tiktok_settings["video_made_with_ai"] = True

    payload: dict[str, Any] = {
        "content": (title or "Bubble wrap").strip()[:90],
        "mediaItems": media_items,
        "platforms": [_tiktok_platform_entry(account_id=tiktok_account_id)],
        "tiktokSettings": tiktok_settings,
        "publishNow": publish_now and not draft,
    }

    body = _request("POST", "/posts", json=payload)
    post = body.get("post") or body.get("data") or body
    post_id = str(post.get("_id") or post.get("id") or body.get("id") or post.get("postId") or "")

    platform_urls: dict[str, str] = {}
    for entry in post.get("platforms") or body.get("platforms") or []:
        if not isinstance(entry, dict):
            continue
        plat = (entry.get("platform") or "").lower()
        url = entry.get("platformPostUrl") or entry.get("postUrl") or ""
        if plat and url:
            platform_urls[plat] = str(url)

    status = str(post.get("status") or body.get("status") or "submitted")
    return ZernioPostResult(
        post_id=post_id,
        status=status,
        message="Zernio posted TikTok photo carousel",
        platform_urls=platform_urls,
    )


def upload_video(
    video_path: Path,
    *,
    caption: str,
    tiktok: bool = True,
    facebook: bool = True,
    publish_now: bool = True,
    tiktok_account_id: str | None = None,
    draft: bool = False,
) -> ZernioPostResult:
    """Presign MP4, upload to Zernio CDN, post to connected platforms."""
    if not credentials_configured():
        raise RuntimeError("ZERNIO_API_KEY not configured")
    if not video_path.exists():
        raise FileNotFoundError(video_path)

    upload_url, public_url = presign_video(video_path)
    upload_file_to_presigned(upload_url, video_path)

    if tiktok and tiktok_account_id:
        platforms = [_tiktok_platform_entry(account_id=tiktok_account_id)]
    else:
        platforms = _platform_targets(tiktok=tiktok, facebook=facebook)

    tiktok_settings: dict[str, Any] = {
        "privacy_level": settings.zernio_tiktok_privacy or "PUBLIC_TO_EVERYONE",
        "allow_comment": True,
        "allow_duet": True,
        "allow_stitch": True,
        "content_preview_confirmed": True,
        "express_consent_given": True,
    }
    if draft:
        tiktok_settings["draft"] = True
    if settings.zernio_declare_aigc:
        tiktok_settings["video_made_with_ai"] = True

    payload: dict[str, Any] = {
        "content": caption[:2200],
        "mediaItems": [{"type": "video", "url": public_url}],
        "platforms": platforms,
        "tiktokSettings": tiktok_settings,
        "publishNow": publish_now and not draft,
    }

    body = _request("POST", "/posts", json=payload)
    post = body.get("post") or body.get("data") or body
    post_id = str(post.get("_id") or post.get("id") or body.get("id") or "")

    platform_urls: dict[str, str] = {}
    for entry in post.get("platforms") or body.get("platforms") or []:
        if not isinstance(entry, dict):
            continue
        plat = (entry.get("platform") or "").lower()
        url = entry.get("platformPostUrl") or entry.get("postUrl") or ""
        if plat and url:
            platform_urls[plat] = str(url)

    status = str(post.get("status") or body.get("status") or "submitted")
    names = ", ".join(p["platform"] for p in payload["platforms"])
    return ZernioPostResult(
        post_id=post_id,
        status=status,
        message=f"Zernio posted to {names}",
        platform_urls=platform_urls,
    )
