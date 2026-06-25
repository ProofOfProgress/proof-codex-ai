"""List channel uploads via YouTube Data API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from shorts_bot.youtube.google_auth import load_credentials_for_manage, load_credentials_for_upload


@dataclass
class ChannelVideo:
    video_id: str
    title: str
    published_at: str


def _youtube_client():
    from googleapiclient.discovery import build

    creds = load_credentials_for_manage() or load_credentials_for_upload()
    if not creds:
        raise RuntimeError(
            "YouTube scope required. Run: "
            "YOUTUBE_OAUTH_UPLOAD=1 python3 -m shorts_bot.youtube.auth_cli"
        )
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def list_channel_videos(*, max_results: int = 200) -> list[ChannelVideo]:
    """Return all videos in the authenticated channel's uploads playlist."""
    youtube = _youtube_client()
    ch = youtube.channels().list(part="contentDetails", mine=True).execute()
    items = ch.get("items") or []
    if not items:
        return []

    uploads_id = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
    videos: list[ChannelVideo] = []
    page_token: str | None = None

    while len(videos) < max_results:
        resp: dict[str, Any] = (
            youtube.playlistItems()
            .list(
                part="snippet",
                playlistId=uploads_id,
                maxResults=min(50, max_results - len(videos)),
                pageToken=page_token,
            )
            .execute()
        )
        for item in resp.get("items") or []:
            sn = item.get("snippet") or {}
            vid = sn.get("resourceId", {}).get("videoId")
            if not vid:
                continue
            videos.append(
                ChannelVideo(
                    video_id=vid,
                    title=(sn.get("title") or vid)[:200],
                    published_at=sn.get("publishedAt") or "",
                )
            )
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return videos
