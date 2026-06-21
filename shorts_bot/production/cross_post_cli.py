"""Upload same MP4 to YouTube + TikTok."""

from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console

console = Console()


def cross_post(
    draft_id: int,
    video_path: Path,
    *,
    tiktok_title: str | None = None,
) -> list[str]:
    from shorts_bot.production.upload_canonical_cli import upload_canonical
    from shorts_bot.tiktok.upload import upload_video_with_refresh

    messages: list[str] = []
    yt_url = upload_canonical(draft_id, video_path)
    messages.append(f"YouTube: {yt_url}")

    title = tiktok_title
    if not title:
        from shorts_bot.memory.store import MemoryStore
        from shorts_bot.config import settings

        draft = MemoryStore(settings.database_path).get_draft(draft_id)
        title = f"{draft.hook} #aitools #techreview"[:2200]

    tt = upload_video_with_refresh(video_path, title=title)
    messages.append(f"TikTok: {tt.status} — {tt.publish_id}")
    return messages


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload draft video to YouTube + TikTok")
    parser.add_argument("--draft-id", type=int, required=True)
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--tiktok-title", default=None, help="Override TikTok caption")
    args = parser.parse_args()

    for line in cross_post(args.draft_id, args.video, tiktok_title=args.tiktok_title):
        console.print(f"[green]{line}[/green]")


if __name__ == "__main__":
    main()
