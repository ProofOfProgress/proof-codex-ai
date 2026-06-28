"""Upload finished MP4 or TikTok photo carousel via Zernio."""

from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload via Zernio (TikTok video or photo carousel)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    video = sub.add_parser("video", help="Upload MP4 video")
    video.add_argument("video", type=Path, help="Path to final_short.mp4")
    video.add_argument("--caption", required=True, help="Caption / title with hashtags")
    video.add_argument("--tiktok-only", action="store_true")
    video.add_argument("--facebook-only", action="store_true")

    carousel = sub.add_parser("carousel", help="Upload 2+ images as TikTok photo carousel")
    carousel.add_argument("images", nargs="+", type=Path, help="PNG/JPG paths in slide order")
    carousel.add_argument("--title", default="Bubble wrap ASMR", help="Photo title (max 90 chars)")
    carousel.add_argument("--description", default="", help="Optional caption below carousel")
    carousel.add_argument("--account-id", default="", help="Zernio TikTok account id")
    carousel.add_argument("--auto-music", action="store_true", help="Let TikTok auto-add music")
    carousel.add_argument("--draft", action="store_true", help="Send to TikTok inbox as draft")

    args = parser.parse_args()

    if args.cmd == "video":
        from shorts_bot.zernio.upload import upload_video

        tiktok = not args.facebook_only
        facebook = not args.tiktok_only
        result = upload_video(args.video, caption=args.caption, tiktok=tiktok, facebook=facebook)
    else:
        from shorts_bot.zernio.upload import upload_photo_carousel

        zid = args.account_id.strip() or None
        result = upload_photo_carousel(
            list(args.images),
            title=args.title,
            description=args.description,
            tiktok_account_id=zid,
            auto_add_music=args.auto_music,
            publish_now=not args.draft,
            draft=args.draft,
        )

    console.print(f"[green]{result.message}[/green]")
    console.print(f"post_id: {result.post_id}")
    console.print(f"status: {result.status}")
    for plat, url in result.platform_urls.items():
        console.print(f"{plat}: {url}")


if __name__ == "__main__":
    main()
