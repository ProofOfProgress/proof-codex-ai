"""Delete videos from the authenticated YouTube channel."""

from __future__ import annotations

from dataclasses import dataclass

from shorts_bot.youtube.channel_videos import ChannelVideo, list_channel_videos
from shorts_bot.youtube.google_auth import load_credentials_for_manage, load_credentials_for_upload


@dataclass
class DeleteResult:
    deleted_ids: list[str]
    failed: list[tuple[str, str]]
    message: str


def delete_video(video_id: str) -> None:
    from googleapiclient.discovery import build

    creds = load_credentials_for_manage() or load_credentials_for_upload()
    if not creds:
        raise RuntimeError(
            "YouTube manage scope required for delete. Re-run: "
            "YOUTUBE_OAUTH_UPLOAD=1 python3 -m shorts_bot.youtube.auth_cli"
        )
    youtube = build("youtube", "v3", credentials=creds, cache_discovery=False)
    youtube.videos().delete(id=video_id).execute()


def delete_all_channel_videos(*, dry_run: bool = False) -> DeleteResult:
    """Delete every video on the authenticated channel."""
    videos = list_channel_videos()
    if dry_run:
        return DeleteResult(
            deleted_ids=[],
            failed=[],
            message=f"Dry run: would delete {len(videos)} video(s).",
        )

    deleted: list[str] = []
    failed: list[tuple[str, str]] = []
    for v in videos:
        try:
            delete_video(v.video_id)
            deleted.append(v.video_id)
        except Exception as exc:
            failed.append((v.video_id, str(exc)[:200]))

    msg = f"Deleted {len(deleted)} video(s)."
    if failed:
        msg += f" Failed {len(failed)}."
    return DeleteResult(deleted_ids=deleted, failed=failed, message=msg)
