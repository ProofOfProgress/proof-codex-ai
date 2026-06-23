"""Upload finished MP4 to TikTok + Facebook via Zernio."""

from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload Short via Zernio (TikTok + Facebook)")
    parser.add_argument("video", type=Path, help="Path to final_short.mp4")
    parser.add_argument("--caption", required=True, help="Caption / title with hashtags")
    parser.add_argument("--tiktok-only", action="store_true")
    parser.add_argument("--facebook-only", action="store_true")
    args = parser.parse_args()

    from shorts_bot.zernio.upload import upload_video

    tiktok = not args.facebook_only
    facebook = not args.tiktok_only
    result = upload_video(args.video, caption=args.caption, tiktok=tiktok, facebook=facebook)
    console.print(f"[green]{result.message}[/green]")
    console.print(f"post_id: {result.post_id}")
    console.print(f"status: {result.status}")
    for plat, url in result.platform_urls.items():
        console.print(f"{plat}: {url}")


if __name__ == "__main__":
    main()
