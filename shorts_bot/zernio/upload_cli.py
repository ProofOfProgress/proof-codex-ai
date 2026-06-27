"""Upload finished MP4 or photo carousel to TikTok via Zernio."""

from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console

console = Console()


def _add_private_flag(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--private",
        action="store_true",
        help="Post as private (SELF_ONLY). Use for all test uploads.",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload to TikTok via Zernio")
    sub = parser.add_subparsers(dest="cmd", required=True)

    video = sub.add_parser("video", help="Upload an MP4 video")
    video.add_argument("video", type=Path, help="Path to final_short.mp4")
    video.add_argument("--caption", required=True, help="Caption / title with hashtags")
    video.add_argument("--tiktok-only", action="store_true")
    video.add_argument("--facebook-only", action="store_true")
    _add_private_flag(video)

    carousel = sub.add_parser("slideshow", help="Upload a 2+ image photo carousel")
    carousel.add_argument("images", type=Path, nargs="+", help="Image paths in slide order")
    carousel.add_argument("--title", required=True, help="Photo title (90 chars max)")
    carousel.add_argument("--caption", default="", help="Full caption / description")
    carousel.add_argument("--account-id", default="", help="Zernio TikTok account id")
    _add_private_flag(carousel)
    carousel.add_argument(
        "--draft",
        action="store_true",
        help="Send to TikTok inbox as draft (often unreliable — prefer --private for tests)",
    )
    carousel.add_argument(
        "--auto-music",
        action="store_true",
        help="Let TikTok add recommended music (not a specific sound)",
    )

    args = parser.parse_args()

    if args.cmd == "video":
        from shorts_bot.zernio.upload import upload_video

        tiktok = not args.facebook_only
        facebook = not args.tiktok_only
        result = upload_video(
            args.video,
            caption=args.caption,
            tiktok=tiktok,
            facebook=facebook,
            private=args.private,
        )
    else:
        from shorts_bot.zernio.upload import upload_photo_carousel

        result = upload_photo_carousel(
            list(args.images),
            title=args.title,
            caption=args.caption,
            tiktok_account_id=args.account_id or None,
            draft=args.draft,
            private=args.private,
            auto_add_music=args.auto_music,
        )

    console.print(f"[green]{result.message}[/green]")
    console.print(f"post_id: {result.post_id}")
    console.print(f"status: {result.status}")
    for plat, url in result.platform_urls.items():
        console.print(f"{plat}: {url}")


if __name__ == "__main__":
    main()
