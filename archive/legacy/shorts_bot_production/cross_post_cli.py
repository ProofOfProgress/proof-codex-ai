"""Upload same MP4 to YouTube (direct API) + TikTok/Facebook (Zernio)."""

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
    youtube: bool = True,
    zernio: bool = True,
) -> list[str]:
    messages: list[str] = []

    if youtube:
        from shorts_bot.production.upload_canonical_cli import upload_canonical

        yt_url = upload_canonical(draft_id, video_path)
        messages.append(f"YouTube: {yt_url}")

    caption = tiktok_title
    if not caption:
        from shorts_bot.config import settings
        from shorts_bot.memory.store import MemoryStore

        draft = MemoryStore(settings.database_path).get_draft(draft_id)
        caption = f"{draft.hook} #aitools #techreview"[:2200]

    if zernio:
        from shorts_bot.zernio.client import credentials_configured
        from shorts_bot.zernio.upload import upload_video

        if not credentials_configured():
            messages.append("Zernio: skipped — ZERNIO_API_KEY missing")
        else:
            result = upload_video(video_path, caption=caption)
            messages.append(f"Zernio: {result.message} (post_id={result.post_id})")
            for plat, url in result.platform_urls.items():
                messages.append(f"  {plat}: {url}")

    return messages


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload draft video to YouTube + Zernio platforms")
    parser.add_argument("--draft-id", type=int, required=True)
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--tiktok-title", default=None, help="Caption for TikTok/Facebook")
    parser.add_argument("--youtube-only", action="store_true")
    parser.add_argument("--zernio-only", action="store_true")
    args = parser.parse_args()

    for line in cross_post(
        args.draft_id,
        args.video,
        tiktok_title=args.tiktok_title,
        youtube=not args.zernio_only,
        zernio=not args.youtube_only,
    ):
        console.print(f"[green]{line}[/green]")


if __name__ == "__main__":
    main()
