from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from shorts_bot.youtube.google_auth import load_credentials


def _services():
    creds = load_credentials()
    if creds is None:
        raise RuntimeError("YouTube not connected. Run: python3 -m shorts_bot.youtube.auth_cli")
    from googleapiclient.discovery import build

    youtube = build("youtube", "v3", credentials=creds, cache_discovery=False)
    analytics = build("youtubeAnalytics", "v2", credentials=creds, cache_discovery=False)
    return youtube, analytics


def get_channel_id() -> str:
    youtube, _ = _services()
    resp = youtube.channels().list(part="id", mine=True).execute()
    items = resp.get("items", [])
    if not items:
        raise RuntimeError("No YouTube channel found on this Google account.")
    return items[0]["id"]


def fetch_video_metrics(days: int = 28, max_videos: int = 20) -> list[dict[str, Any]]:
    """Pull official YouTube Analytics metrics per video."""
    _, analytics = _services()
    end = date.today()
    start = end - timedelta(days=days)

    resp = (
        analytics.reports()
        .query(
            ids="channel==MINE",
            startDate=start.isoformat(),
            endDate=end.isoformat(),
            metrics="views,likes,comments,averageViewPercentage",
            dimensions="video",
            sort="-views",
            maxResults=max_videos,
        )
        .execute()
    )

    headers = [h["name"] for h in resp.get("columnHeaders", [])]
    rows = resp.get("rows", [])
    results: list[dict[str, Any]] = []
    for row in rows:
        data = dict(zip(headers, row))
        video_id = str(data.get("video", "unknown"))
        avg_pct = float(data.get("averageViewPercentage", 0) or 0)
        results.append(
            {
                "video_id": video_id,
                "video_label": video_id,
                "title": video_id,
                "views": int(float(data.get("views", 0) or 0)),
                "likes": int(float(data.get("likes", 0) or 0)),
                "comments": int(float(data.get("comments", 0) or 0)),
                "retention_rate": avg_pct,
                # Real Shorts "viewed vs swiped away" is Studio-only — not in Analytics API.
                # Do not guess; RewardEngine scores retention/views when swipe is absent.
                "swipe_source": "unavailable",
            }
        )
    return results


def enrich_titles(metrics: list[dict[str, Any]]) -> list[dict[str, Any]]:
    youtube, _ = _services()
    ids = [m["video_id"] for m in metrics if m.get("video_id")]
    if not ids:
        return metrics
    resp = (
        youtube.videos()
        .list(part="snippet", id=",".join(ids[:50]))
        .execute()
    )
    titles = {item["id"]: item["snippet"]["title"] for item in resp.get("items", [])}
    for m in metrics:
        title = titles.get(m["video_id"], m["video_id"])
        m["title"] = title
        m["video_label"] = title[:80]
    return metrics
