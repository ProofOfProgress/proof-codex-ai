"""Fetch and reply to YouTube comments via Data API."""

from __future__ import annotations

from dataclasses import dataclass

from shorts_bot.youtube.channel_api import get_my_channel_id
from shorts_bot.youtube.google_auth import load_credentials_for_manage, load_credentials_for_upload


@dataclass
class CommentThread:
    thread_id: str
    top_comment_id: str
    video_id: str
    video_title: str
    author: str
    author_channel_id: str | None
    text: str
    published_at: str
    channel_has_replied: bool


def _youtube():
    from googleapiclient.discovery import build

    creds = load_credentials_for_manage() or load_credentials_for_upload()
    if not creds:
        raise RuntimeError(
            "YouTube comment access needs upload/force-ssl OAuth. "
            "Run: YOUTUBE_OAUTH_UPLOAD=1 python3 -m shorts_bot.youtube.auth_cli"
        )
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def comments_ready() -> bool:
    return bool(load_credentials_for_manage() or load_credentials_for_upload())


def fetch_recent_threads(*, max_results: int = 40) -> list[CommentThread]:
    yt = _youtube()
    my_channel_id = get_my_channel_id()

    video_titles: dict[str, str] = {}
    threads: list[CommentThread] = []

    resp = (
        yt.commentThreads()
        .list(
            part="snippet,replies",
            allThreadsRelatedToChannelId=my_channel_id,
            order="time",
            maxResults=min(max_results, 100),
            textFormat="plainText",
        )
        .execute()
    )

    for item in resp.get("items") or []:
        snippet = item.get("snippet") or {}
        top = (snippet.get("topLevelComment") or {}).get("snippet") or {}
        thread_id = item["id"]
        top_id = (snippet.get("topLevelComment") or {}).get("id") or thread_id
        video_id = snippet.get("videoId") or ""
        author = (top.get("authorDisplayName") or "viewer").strip()
        author_cid = top.get("authorChannelId", {}).get("value")
        text = (top.get("textDisplay") or top.get("textOriginal") or "").strip()
        published = top.get("publishedAt") or ""

        channel_has_replied = False
        replies = (item.get("replies") or {}).get("comments") or []
        for reply in replies:
            rs = reply.get("snippet") or {}
            if rs.get("authorChannelId", {}).get("value") == my_channel_id:
                channel_has_replied = True
                break

        if not video_id:
            continue
        if video_id not in video_titles:
            video_titles[video_id] = _video_title(yt, video_id)

        threads.append(
            CommentThread(
                thread_id=thread_id,
                top_comment_id=top_id,
                video_id=video_id,
                video_title=video_titles[video_id],
                author=author,
                author_channel_id=author_cid,
                text=text,
                published_at=published,
                channel_has_replied=channel_has_replied,
            )
        )
    return threads


def _video_title(yt, video_id: str) -> str:
    try:
        resp = yt.videos().list(part="snippet", id=video_id).execute()
        items = resp.get("items") or []
        if items:
            return (items[0].get("snippet") or {}).get("title") or video_id
    except Exception:
        pass
    return video_id


def post_reply(parent_comment_id: str, text: str) -> str:
    yt = _youtube()
    body = {"snippet": {"parentId": parent_comment_id, "textOriginal": text[:9000]}}
    resp = yt.comments().insert(part="snippet", body=body).execute()
    return resp.get("id") or ""
