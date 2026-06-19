"""Upload a finished MP4 to TikTok."""

from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload Short to TikTok")
    parser.add_argument("video", type=Path, help="Path to final_short.mp4")
    parser.add_argument("--title", required=True, help="Caption (hashtags OK)")
    parser.add_argument(
        "--privacy",
        default=None,
        help="PUBLIC_TO_EVERYONE | SELF_ONLY | ... (default: auto from creator_info)",
    )
    args = parser.parse_args()

    from shorts_bot.tiktok.upload import upload_video_with_refresh

    result = upload_video_with_refresh(
        args.video,
        title=args.title,
        privacy_level=args.privacy,
    )
    console.print(f"[green]{result.message}[/green]")
    console.print(f"publish_id: {result.publish_id}")
    console.print(f"status: {result.status}")


if __name__ == "__main__":
    main()
