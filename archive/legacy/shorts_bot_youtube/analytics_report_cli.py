"""Honest YouTube analytics report — what we know vs what we don't."""

from __future__ import annotations

import argparse
import json

from rich.console import Console
from rich.table import Table

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(description="Show honest analytics (API limits labeled)")
    parser.add_argument("--sync", action="store_true", help="Run sync first")
    parser.add_argument("--days", type=int, default=28)
    args = parser.parse_args()

    from shorts_bot.config import settings
    from shorts_bot.memory.extensions import MemoryExtensions
    from shorts_bot.memory.store import MemoryStore

    mem = MemoryExtensions(MemoryStore(settings.database_path))

    if args.sync:
        from shorts_bot.training.proposer import ImprovementProposer
        from shorts_bot.youtube.sync import AnalyticsSync

        result = AnalyticsSync(mem, ImprovementProposer(mem)).run(days=args.days)
        console.print(result.message)

    rows = mem.list_analytics(limit=20)
    if not rows:
        console.print("[yellow]No analytics stored yet. Upload a Short then run with --sync[/yellow]")
        return

    table = Table(title=f"Analytics (honest — last {args.days}d API window unless noted)")
    table.add_column("Video")
    table.add_column("Views")
    table.add_column("Avg watch %")
    table.add_column("Swipe")
    table.add_column("Source")
    for row in rows:
        m = row["metrics"]
        title = (m.get("title") or row["video_label"])[:42]
        views = str(m.get("views", "—"))
        avg = m.get("average_view_percentage", m.get("retention_rate"))
        avg_s = f"{float(avg):.0f}%" if avg else "—"
        swipe = m.get("viewed_vs_swiped_away")
        swipe_s = f"{float(swipe):.0f}%" if swipe else "N/A"
        swipe_src = m.get("swipe_source", "—")
        src = m.get("metrics_source", "—")
        window = m.get("metrics_window_days")
        if window:
            src = f"{src} ({window}d)"
        table.add_row(title, views, avg_s, f"{swipe_s} ({swipe_src})", src)

    console.print(table)
    console.print(
        "\n[dim]Swipe-away = Studio only (not in Google Analytics API). "
        "Avg watch % ≠ Studio retention graph. Add Studio numbers: POST /api/score[/dim]"
    )

    rewards = mem.recent_rewards(limit=5)
    if rewards:
        console.print("\n[bold]Recent scores[/bold]")
        for r in rewards:
            console.print(f"  {r['verdict']:7} {r['video_label'][:40]} — {r['reason'][:80]}")


if __name__ == "__main__":
    main()
