"""CLI: Gemini production review for a rendered Short."""

from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console

from shorts_bot.config import settings
from shorts_bot.production.video_production_review import run_production_review

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(description="Gemini production review for Don't Blink Short")
    parser.add_argument("--draft-id", type=int, required=True)
    parser.add_argument("--video", type=Path, default=None, help="MP4 path (default: pack final_short_unlisted.mp4)")
    parser.add_argument("--no-cache", action="store_true")
    args = parser.parse_args()

    pack_dir = settings.data_dir / "production" / f"draft_{args.draft_id}"
    video = args.video or (pack_dir / "final_short_unlisted.mp4")
    if not video.exists():
        video = pack_dir / "final_short.mp4"

    console.print(f"[cyan]Reviewing {video}…[/cyan]")
    review = run_production_review(video, pack_dir, use_cache=not args.no_cache)
    console.print(f"[bold]Score {review.score}/10[/bold] (concept {review.concept_score}, production {review.production_score})")
    console.print(review.summary)
    console.print(f"\n[yellow]AV sync:[/yellow] {review.av_sync}")
    console.print(f"[yellow]Jumpscare:[/yellow] {review.jumpscare}")
    console.print(f"[yellow]Captions:[/yellow] {review.captions}")
    console.print(f"[yellow]Visuals:[/yellow] {review.visuals}")
    if review.weird_frames:
        console.print("\n[red]Weird frames:[/red]")
        for w in review.weird_frames:
            console.print(f"  - {w}")
    if review.fixes:
        console.print("\n[green]Fixes:[/green]")
        for f in review.fixes:
            console.print(f"  - {f}")
    console.print(f"\nSaved → {pack_dir / 'gemini_review.json'}")


if __name__ == "__main__":
    main()
