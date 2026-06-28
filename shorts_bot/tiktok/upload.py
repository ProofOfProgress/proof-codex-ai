"""Upload MP4 to TikTok via Content Posting API (FILE_UPLOAD)."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

from shorts_bot.config import settings
from shorts_bot.tiktok.oauth import get_access_token, refresh_access_token
from shorts_bot.tiktok_shop.upload_guard import require_pre_publish

API_BASE = "https://open.tiktokapis.com"


@dataclass
class TikTokUploadResult:
    publish_id: str
    status: str
    message: str


def _api_post(
    path: str,
    payload: dict[str, Any],
    *,
    token: str | None = None,
    token_path: Path | None = None,
) -> dict[str, Any]:
    access = token or get_access_token(path=token_path)
    with httpx.Client(timeout=120.0) as client:
        resp = client.post(
            f"{API_BASE}{path}",
            json=payload,
            headers={
                "Authorization": f"Bearer {access}",
                "Content-Type": "application/json; charset=UTF-8",
            },
        )
    try:
        body = resp.json()
    except Exception as exc:
        raise RuntimeError(f"TikTok API non-JSON ({resp.status_code}): {resp.text[:300]}") from exc
    err = body.get("error") or {}
    if resp.status_code >= 400 or (isinstance(err, dict) and err.get("code") not in (None, "ok")):
        code = err.get("code") if isinstance(err, dict) else err
        msg = err.get("message") if isinstance(err, dict) else resp.text
        raise RuntimeError(f"TikTok API error {code}: {msg}")
    return body


def query_creator_info(*, token: str | None = None, token_path: Path | None = None) -> dict[str, Any]:
    body = _api_post("/v2/post/publish/creator_info/query/", {}, token=token, token_path=token_path)
    return body.get("data") or {}


def _pick_privacy(creator: dict[str, Any]) -> str:
    options = creator.get("privacy_level_options") or []
    preferred = (settings.tiktok_privacy_level or "").strip()
    if preferred and preferred in options:
        return preferred
    for candidate in (
        "PUBLIC_TO_EVERYONE",
        "MUTUAL_FOLLOW_FRIENDS",
        "FOLLOWER_OF_CREATOR",
        "SELF_ONLY",
    ):
        if candidate in options:
            return candidate
    if options:
        return str(options[0])
    return "SELF_ONLY"


def upload_video(
    video_path: Path,
    *,
    title: str,
    privacy_level: str | None = None,
    is_aigc: bool | None = None,
    brand_organic: bool = False,
    poll_timeout_sec: int = 300,
    token_path: Path | None = None,
    product: str = "",
    shop_account_id: str = "",
    pre_publish_tier: str | None = None,
    skip_pre_publish: bool = False,
) -> TikTokUploadResult:
    """Direct post via video.publish — FILE_UPLOAD + status poll."""
    if not video_path.exists():
        raise FileNotFoundError(video_path)

    require_pre_publish(
        "video",
        video_path=video_path,
        caption=title,
        product=product,
        shop_account_id=shop_account_id,
        tier=pre_publish_tier,
        skip=skip_pre_publish,
    )

    size = video_path.stat().st_size
    token = get_access_token(path=token_path)
    creator = query_creator_info(token=token, token_path=token_path)
    privacy = privacy_level or _pick_privacy(creator)

    init_body = _api_post(
        "/v2/post/publish/video/init/",
        {
            "post_info": {
                "title": title[:2200],
                "privacy_level": privacy,
                "disable_duet": bool(settings.tiktok_disable_duet),
                "disable_stitch": bool(settings.tiktok_disable_stitch),
                "disable_comment": bool(settings.tiktok_disable_comment),
                "brand_content_toggle": False,
                "brand_organic_toggle": brand_organic,
                "is_aigc": settings.tiktok_declare_aigc if is_aigc is None else is_aigc,
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": size,
                "chunk_size": size,
                "total_chunk_count": 1,
            },
        },
        token=token,
        token_path=token_path,
    )
    data = init_body.get("data") or {}
    publish_id = data.get("publish_id")
    upload_url = data.get("upload_url")
    if not publish_id or not upload_url:
        raise RuntimeError(f"TikTok init missing publish_id/upload_url: {init_body}")

    raw = video_path.read_bytes()
    with httpx.Client(timeout=600.0) as client:
        put = client.put(
            upload_url,
            content=raw,
            headers={
                "Content-Type": "video/mp4",
                "Content-Length": str(size),
                "Content-Range": f"bytes 0-{size - 1}/{size}",
            },
        )
    if put.status_code not in (200, 201, 204):
        raise RuntimeError(f"TikTok file upload failed ({put.status_code}): {put.text[:300]}")

    deadline = time.time() + poll_timeout_sec
    last_status = "PROCESSING"
    while time.time() < deadline:
        status_body = _api_post(
            "/v2/post/publish/status/fetch/",
            {"publish_id": publish_id},
            token=token,
            token_path=token_path,
        )
        sdata = status_body.get("data") or {}
        last_status = (sdata.get("status") or "UNKNOWN").upper()
        if last_status in ("PUBLISH_COMPLETE", "PUBLISHED"):
            return TikTokUploadResult(
                publish_id=publish_id,
                status=last_status,
                message=f"TikTok publish complete ({privacy})",
            )
        if last_status in ("FAILED", "PUBLISH_FAILED"):
            reason = sdata.get("fail_reason") or sdata
            raise RuntimeError(f"TikTok publish failed: {reason}")
        time.sleep(5)

    return TikTokUploadResult(
        publish_id=publish_id,
        status=last_status,
        message=f"TikTok still processing after {poll_timeout_sec}s — publish_id={publish_id}",
    )


def upload_video_with_refresh(video_path: Path, **kwargs: Any) -> TikTokUploadResult:
    try:
        return upload_video(video_path, **kwargs)
    except RuntimeError as exc:
        if "access_token_invalid" in str(exc).lower() or "401" in str(exc):
            refresh_access_token()
            return upload_video(video_path, **kwargs)
        raise
