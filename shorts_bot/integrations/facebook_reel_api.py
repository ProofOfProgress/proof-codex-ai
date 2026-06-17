"""Facebook Page Reel upload via Meta Graph API (resumable upload)."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from shorts_bot.integrations.facebook_credentials import resolve_facebook_credentials

GRAPH = "https://graph.facebook.com/v21.0"


@dataclass
class FacebookReelResult:
    video_id: str
    post_id: str | None
    message: str


def _post_form(url: str, data: dict) -> dict:
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode())


def _upload_binary(upload_url: str, video_path: Path, *, access_token: str) -> None:
    data = video_path.read_bytes()
    req = urllib.request.Request(
        upload_url,
        data=data,
        headers={
            "Authorization": f"OAuth {access_token}",
            "Content-Type": "application/octet-stream",
            "offset": "0",
            "file_size": str(len(data)),
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=600) as resp:
        resp.read()


def upload_facebook_reel(
    video_path: Path,
    *,
    description: str,
    title: str = "",
    page_id: str | None = None,
    access_token: str | None = None,
) -> FacebookReelResult:
    """Three-step Reel publish: start → upload binary → finish."""
    pid = (page_id or "").strip() or resolve_facebook_credentials()[0]
    token = (access_token or "").strip() or resolve_facebook_credentials()[1]
    if not pid or not token:
        raise RuntimeError(
            "Set FACEBOOK_PAGE_ID and META_PAGE_ACCESS_TOKEN in Cursor Secrets "
            "(Page token from Meta Graph API Explorer)."
        )
    if not video_path.is_file():
        raise FileNotFoundError(video_path)

    start = _post_form(
        f"{GRAPH}/{pid}/video_reels",
        {"upload_phase": "start", "access_token": token},
    )
    video_id = str(start.get("video_id") or "")
    upload_url = str(start.get("upload_url") or "")
    if not video_id or not upload_url:
        raise RuntimeError(f"Facebook Reel start failed: {start}")

    _upload_binary(upload_url, video_path, access_token=token)

    finish = _post_form(
        f"{GRAPH}/{pid}/video_reels",
        {
            "upload_phase": "finish",
            "video_id": video_id,
            "video_state": "PUBLISHED",
            "description": description[:2200],
            "title": (title or description)[:100],
            "access_token": token,
        },
    )
    post_id = finish.get("post_id") or finish.get("id")
    return FacebookReelResult(
        video_id=video_id,
        post_id=str(post_id) if post_id else None,
        message=f"Facebook Reel published (video_id={video_id})",
    )


def probe_facebook_reel_api(
    *,
    page_id: str | None = None,
    access_token: str | None = None,
) -> tuple[bool, str]:
    pid = (page_id or "").strip() or resolve_facebook_credentials()[0]
    token = (access_token or "").strip() or resolve_facebook_credentials()[1]
    if not pid or not token:
        return False, "FACEBOOK_PAGE_ID + META_PAGE_ACCESS_TOKEN not set"
    url = f"{GRAPH}/{pid}?fields=name,id&access_token={urllib.parse.quote(token)}"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = json.loads(resp.read().decode())
        return True, f"Facebook Page OK — {data.get('name', pid)}"
    except urllib.error.HTTPError as exc:
        return False, f"Facebook API {exc.code}: {exc.read().decode()[:200]}"
