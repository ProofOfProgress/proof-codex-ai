"""Default ritual: review last uploads — good and bad metrics."""

from __future__ import annotations

import argparse

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Review last uploads — good + bad metrics (owner default check)"
    )
    parser.add_argument("--limit", type=int, default=5, help="How many recent uploads")
    parser.add_argument("--no-sync", action="store_true", help="Skip API sync (use cached data)")
    parser.add_argument("--days", type=int, default=28, help="Analytics API window")
    args = parser.parse_args()

    from shorts_bot.youtube.analytics_review import review_last_uploads

    review = review_last_uploads(
        limit=args.limit,
        sync=not args.no_sync,
        days=args.days,
    )

    console.print(Panel(review.summary, title="Last uploads analytics", border_style="cyan"))

    if not review.videos:
        return

    table = Table()
    table.add_column("Video")
    table.add_column("Views")
    table.add_column("Watch %")
    table.add_column("Verdict")
    table.add_column("Good")
    table.add_column("Bad")
    for v in review.videos:
        table.add_row(
            v.title[:40],
            str(v.views),
            f"{v.avg_watch_pct:.0f}%" if v.avg_watch_pct is not None else "—",
            v.verdict,
            "; ".join(v.goods[:2]) or "—",
            "; ".join(v.bads[:2]) or "—",
        )
    console.print(table)

    for v in review.videos:
        if v.notes:
            console.print(f"[dim]{v.title[:35]}…[/dim] " + " · ".join(v.notes[:2]))


if __name__ == "__main__":
    main()
