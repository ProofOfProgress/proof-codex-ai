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


def _tiktok_privacy(*, private: bool = False) -> str:
    if private:
        return "SELF_ONLY"
    return settings.zernio_tiktok_privacy or "PUBLIC_TO_EVERYONE"


def upload_video(
    video_path: Path,
    *,
    caption: str,
    tiktok: bool = True,
    facebook: bool = True,
    publish_now: bool = True,
    private: bool = False,
) -> ZernioPostResult:
    """Presign MP4, upload to Zernio CDN, post to connected platforms."""
    if not credentials_configured():
        raise RuntimeError("ZERNIO_API_KEY not configured")
    if not video_path.exists():
        raise FileNotFoundError(video_path)

    upload_url, public_url = presign_video(video_path)
    upload_file_to_presigned(upload_url, video_path)

    payload: dict[str, Any] = {
        "content": caption[:2200],
        "mediaItems": [{"type": "video", "url": public_url}],
        "platforms": _platform_targets(tiktok=tiktok, facebook=facebook),
        "tiktokSettings": {
            "privacy_level": _tiktok_privacy(private=private),
            "allow_comment": True,
            "allow_duet": True,
            "allow_stitch": True,
            "content_preview_confirmed": True,
            "express_consent_given": True,
        },
        "publishNow": publish_now,
    }
    if settings.zernio_declare_aigc:
        payload["tiktokSettings"]["video_made_with_ai"] = True

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
    vis = "private" if private else "public"
    return ZernioPostResult(
        post_id=post_id,
        status=status,
        message=f"Zernio posted to {names} ({vis})",
        platform_urls=platform_urls,
    )


def upload_photo_carousel(
    image_paths: list[Path],
    *,
    title: str,
    caption: str = "",
    tiktok_account_id: str | None = None,
    tiktok: bool = True,
    facebook: bool = False,
    publish_now: bool = True,
    draft: bool = False,
    private: bool = False,
    auto_add_music: bool = False,
) -> ZernioPostResult:
    """Upload 2+ images as a TikTok photo carousel via Zernio."""
    if not credentials_configured():
        raise RuntimeError("ZERNIO_API_KEY not configured")
    if len(image_paths) < 2:
        raise ValueError("Photo carousel requires at least 2 images")
    if len(image_paths) > 35:
        raise ValueError("TikTok photo carousel supports at most 35 images")

    media_items: list[dict[str, str]] = []
    for path in image_paths:
        if not path.exists():
            raise FileNotFoundError(path)
        upload_url, public_url = presign_media(path)
        upload_file_to_presigned(upload_url, path)
        media_items.append({"type": "image", "url": public_url})

    tid = (tiktok_account_id or "").strip() or account_id_for("tiktok")
    if tiktok and not tid:
        raise RuntimeError("No TikTok account on Zernio — connect in zernio.com dashboard")

    platforms: list[dict[str, Any]] = []
    if tiktok:
        platforms.append({"platform": "tiktok", "accountId": tid})
    if facebook:
        platforms.extend(_platform_targets(tiktok=False, facebook=True))
    if not platforms:
        raise RuntimeError("No Zernio platforms enabled for photo carousel")

    tiktok_settings: dict[str, Any] = {
        "privacy_level": _tiktok_privacy(private=private),
        "allow_comment": True,
        "media_type": "photo",
        "photo_cover_index": 0,
        "content_preview_confirmed": True,
        "express_consent_given": True,
        "auto_add_music": auto_add_music,
    }
    if caption.strip():
        tiktok_settings["description"] = caption.strip()[:4000]
    if draft:
        tiktok_settings["draft"] = True
    if settings.zernio_declare_aigc:
        tiktok_settings["video_made_with_ai"] = True

    payload: dict[str, Any] = {
        "content": title.strip()[:90],
        "mediaItems": media_items,
        "platforms": platforms,
        "tiktokSettings": tiktok_settings,
        "publishNow": publish_now,
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
    if draft:
        mode = "draft inbox"
    elif private:
        mode = "private"
    else:
        mode = "public"
    return ZernioPostResult(
        post_id=post_id,
        status=status,
        message=f"Zernio photo carousel {mode} → TikTok ({len(image_paths)} images)",
        platform_urls=platform_urls,
    )
