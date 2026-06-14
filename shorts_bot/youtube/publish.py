"""Scheduled unlisted → public flip via YouTube Data API."""

from __future__ import annotations

from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.youtube.google_auth import load_credentials_for_upload


def declare_synthetic_media(video_id: str, *, enabled: bool = True) -> str:
    """Set YouTube altered/synthetic (AI) disclosure on an existing video."""
    from googleapiclient.discovery import build

    creds = load_credentials_for_upload()
    if not creds:
        raise RuntimeError("YouTube upload scope required")
    youtube = build("youtube", "v3", credentials=creds)
    youtube.videos().update(
        part="status",
        body={"id": video_id, "status": {"containsSyntheticMedia": enabled}},
    ).execute()
    label = "on" if enabled else "off"
    return f"AI disclosure {label} for {video_id}"


def delete_video(video_id: str) -> str:
    from googleapiclient.discovery import build

    creds = load_credentials_for_upload()
    if not creds:
        raise RuntimeError("YouTube upload scope required for delete")
    youtube = build("youtube", "v3", credentials=creds)
    youtube.videos().delete(id=video_id).execute()
    return f"Deleted {video_id}"


def update_video_visibility(video_id: str, visibility: str = "public") -> str:
    from googleapiclient.discovery import build

    creds = load_credentials_for_upload()
    if not creds:
        raise RuntimeError("YouTube upload scope required for publish")
    youtube = build("youtube", "v3", credentials=creds)
    youtube.videos().update(
        part="status",
        body={"id": video_id, "status": {"privacyStatus": visibility}},
    ).execute()
    return f"Set {video_id} to {visibility}"


def publish_due_videos(memory: MemoryExtensions) -> list[str]:
    """Publish videos whose publish_at has passed. Returns video_ids published."""
    published: list[str] = []
    for row in memory.list_due_scheduled_publishes():
        try:
            update_video_visibility(row["video_id"], "public")
            memory.mark_scheduled_published(row["video_id"])
            published.append(row["video_id"])
        except Exception:
            continue
    return published
