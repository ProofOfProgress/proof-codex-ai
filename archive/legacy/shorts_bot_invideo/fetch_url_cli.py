"""Fetch InVideo export from a share link — no file attach in Cursor needed."""

from __future__ import annotations

import argparse

from rich.console import Console
from rich.panel import Panel

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download MP4 from Google Drive / Dropbox / direct URL into draft pack"
    )
    parser.add_argument("--draft-id", type=int, required=True)
    parser.add_argument("url", help="Share link to the exported MP4")
    args = parser.parse_args()

    console.print(
        Panel(
            "Use this when you can't attach files in Cursor.\n"
            "Download the video on your laptop → upload to Drive → paste the link here.",
            title="Import from link",
        )
    )

    from shorts_bot.invideo.fetch_url import fetch_for_draft

    try:
        dest = fetch_for_draft(args.draft_id, args.url)
    except Exception as exc:
        console.print(f"[red]{exc}[/red]")
        raise SystemExit(1) from exc

    console.print(f"[green]Saved:[/green] {dest}")
    console.print(
        f"\nUpload: python3 -m shorts_bot.production.upload_canonical_cli "
        f"--draft-id {args.draft_id} --video {dest}"
    )


if __name__ == "__main__":
    main()
