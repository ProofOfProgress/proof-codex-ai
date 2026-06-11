"""YouTube Data API — competitor Short titles for research."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CompetitorVideo:
    title: str
    channel: str
    video_id: str


def search_competitor_shorts(topic: str, *, max_results: int = 8) -> list[CompetitorVideo]:
    """Return recent Short-style videos for a topic via YouTube Data API."""
    from shorts_bot.youtube.google_auth import load_credentials, load_credentials_for_upload

    creds = load_credentials_for_upload() or load_credentials()
    if not creds:
        return []

    try:
        from googleapiclient.discovery import build

        youtube = build("youtube", "v3", credentials=creds, cache_discovery=False)
        response = (
            youtube.search()
            .list(
                q=f"{topic} #shorts",
                part="snippet",
                type="video",
                videoDuration="short",
                maxResults=max_results,
                order="relevance",
                safeSearch="moderate",
            )
            .execute()
        )
    except Exception:
        return []

    out: list[CompetitorVideo] = []
    for item in response.get("items") or []:
        sn = item.get("snippet") or {}
        title = str(sn.get("title", "")).strip()
        channel = str(sn.get("channelTitle", "")).strip()
        vid = str(item.get("id", {}).get("videoId", "")).strip()
        if title:
            out.append(CompetitorVideo(title=title, channel=channel, video_id=vid))
    return out


def competitor_context_block(videos: list[CompetitorVideo], *, max_chars: int = 2000) -> str:
    if not videos:
        return ""
    lines = ["YOUTUBE COMPETITOR SHORTS (real titles — find the gap):"]
    for v in videos:
        lines.append(f"- {v.title} — {v.channel}")
    return "\n".join(lines)[:max_chars]
