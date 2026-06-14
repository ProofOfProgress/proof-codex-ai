"""Upload Short to YouTube via Data API (resumable upload)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.youtube.google_auth import load_credentials_for_upload, upload_ready as youtube_upload_ready


@dataclass
class UploadResult:
    video_id: str
    video_url: str
    message: str


def _upload_mp4(
    video_path: Path,
    *,
    title: str,
    description: str,
    tags: list[str],
    visibility: str,
    url_template: str,
    publish_at: datetime | None = None,
) -> UploadResult:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    if not video_path.exists():
        raise FileNotFoundError(video_path)

    creds = load_credentials_for_upload()
    if not creds:
        raise RuntimeError(
            "YouTube upload not authorized. Re-run: python3 -m shorts_bot.youtube.auth_cli "
            "(needs youtube.upload scope)"
        )

    youtube = build("youtube", "v3", credentials=creds)
    status_body: dict = {
        "privacyStatus": visibility if visibility in ("public", "unlisted", "private") else "unlisted",
        "selfDeclaredMadeForKids": False,
    }
    if publish_at is not None:
        if publish_at.tzinfo is None:
            publish_at = publish_at.replace(tzinfo=timezone.utc)
        status_body["privacyStatus"] = "private"
        status_body["publishAt"] = publish_at.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags[:30],
            "categoryId": (settings.youtube_category_id or "24")[:2],
        },
        "status": status_body,
    }
    if settings.youtube_declare_synthetic_media:
        body["status"]["containsSyntheticMedia"] = True

    media = MediaFileUpload(
        str(video_path),
        mimetype="video/mp4",
        resumable=True,
        chunksize=1024 * 1024,
    )
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            pass
    vid = response["id"]
    url = url_template.format(vid=vid)
    sched = status_body.get("publishAt", "")
    msg = f"Uploaded to YouTube ({status_body['privacyStatus']})"
    if sched:
        msg += f", scheduled public at {sched}"
    msg += f": {url}"
    return UploadResult(
        video_id=vid,
        video_url=url,
        message=msg,
    )


def upload_short(
    video_path: Path,
    *,
    title: str,
    description: str,
    tags: list[str],
    visibility: str = "unlisted",
    publish_at: datetime | None = None,
) -> UploadResult:
    """Upload MP4 as YouTube Short. Requires youtube.upload OAuth scope."""
    return _upload_mp4(
        video_path,
        title=title,
        description=description,
        tags=tags,
        visibility=visibility,
        url_template="https://youtube.com/shorts/{vid}",
        publish_at=publish_at,
    )


def upload_video(
    video_path: Path,
    *,
    title: str,
    description: str,
    tags: list[str],
    visibility: str = "unlisted",
) -> UploadResult:
    """Upload MP4 as standard long-form video (16:9). Same API as Shorts."""
    return _upload_mp4(
        video_path,
        title=title,
        description=description,
        tags=tags,
        visibility=visibility,
        url_template="https://youtube.com/watch?v={vid}",
    )


def upload_ready() -> bool:
    return youtube_upload_ready()
