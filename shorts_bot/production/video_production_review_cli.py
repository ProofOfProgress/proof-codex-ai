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
    parser.add_argument(
        "--deep",
        action="store_true",
        help="Dense frame sample + VO/subtitle/glitch/framing audit",
    )
    args = parser.parse_args()

    pack_dir = settings.data_dir / "production" / f"draft_{args.draft_id}"
    video = args.video or (pack_dir / "final_short_unlisted.mp4")
    if not video.exists():
        video = pack_dir / "final_short.mp4"

    console.print(f"[cyan]Reviewing {video}…[/cyan]")
    review = run_production_review(
        video, pack_dir, use_cache=not args.no_cache, deep=args.deep
    )
    console.print(
        f"[bold]Score {review.score:.0f}/100[/bold] "
        f"(concept {review.concept_score:.0f}, production {review.production_score:.0f})"
    )
    console.print(review.summary)
    console.print(f"\n[yellow]AV sync:[/yellow] {review.av_sync}")
    if review.vo_visual_match:
        console.print(f"[yellow]VO vs video:[/yellow] {review.vo_visual_match}")
    if review.subtitle_sync:
        console.print(f"[yellow]Subtitle sync:[/yellow] {review.subtitle_sync}")
    console.print(f"[yellow]Jumpscare:[/yellow] {review.jumpscare}")
    console.print(f"[yellow]Captions:[/yellow] {review.captions}")
    console.print(f"[yellow]Visuals:[/yellow] {review.visuals}")
    for label, items in (
        ("Visual glitches", review.visual_glitches),
        ("Framing issues", review.framing_issues),
        ("Shouldn't be there", review.things_that_shouldnt_be_there),
        ("Nonsensical", review.nonsensical_elements),
        ("Weird frames", review.weird_frames),
    ):
        if items:
            console.print(f"\n[red]{label}:[/red]")
            for w in items:
                console.print(f"  - {w}")
    if review.fixes:
        console.print("\n[green]Fixes:[/green]")
        for f in review.fixes:
            console.print(f"  - {f}")
    out = "gemini_deep_review.json" if args.deep else "gemini_review.json"
    console.print(f"\nSaved → {pack_dir / out}")


if __name__ == "__main__":
    main()
