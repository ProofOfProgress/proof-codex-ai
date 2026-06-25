"""CLI: list best Short drafts for compilation."""

from __future__ import annotations

import argparse

from rich.console import Console
from rich.table import Table

from shorts_bot.production.winner_selection import list_draft_candidates, pick_compilation_drafts

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(description="Pick best Shorts for long compilation")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument(
        "--draft-ids",
        type=str,
        default="",
        help="Score specific drafts (comma-separated)",
    )
    args = parser.parse_args()

    if args.draft_ids.strip():
        ids = [int(x.strip()) for x in args.draft_ids.split(",") if x.strip()]
        candidates = pick_compilation_drafts(draft_ids=ids)
    else:
        candidates = list_draft_candidates(limit=args.limit)

    table = Table(title="Compilation candidates")
    table.add_column("Draft")
    table.add_column("Score")
    table.add_column("Dur")
    table.add_column("Uploaded")
    table.add_column("Hook")
    table.add_column("Reasons")

    for c in candidates:
        table.add_row(
            str(c.draft_id),
            f"{c.score:.0f}",
            f"{c.duration_seconds:.1f}s",
            "yes" if c.uploaded else "no",
            (c.hook or c.topic)[:48],
            "; ".join(c.reasons[:2]),
        )

    console.print(table)


if __name__ == "__main__":
    main()
