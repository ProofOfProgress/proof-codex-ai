"""Upload Short to YouTube via Data API (resumable upload)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from shorts_bot.youtube.google_auth import load_credentials_for_upload


@dataclass
class UploadResult:
    video_id: str
    video_url: str
    message: str


def upload_short(
    video_path: Path,
    *,
    title: str,
    description: str,
    tags: list[str],
    visibility: str = "unlisted",
) -> UploadResult:
    """Upload MP4 as YouTube Short. Requires youtube.upload OAuth scope."""
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
    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags[:30],
            "categoryId": "22",  # People & Blogs — fine for self-help Shorts
        },
        "status": {
            "privacyStatus": visibility if visibility in ("public", "unlisted", "private") else "unlisted",
            "selfDeclaredMadeForKids": False,
        },
    }

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
    url = f"https://youtube.com/shorts/{vid}"
    return UploadResult(
        video_id=vid,
        video_url=url,
        message=f"Uploaded to YouTube ({visibility}): {url}",
    )


def upload_ready() -> bool:
    return bool(load_credentials_for_upload())
