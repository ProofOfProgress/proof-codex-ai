"""CLI: expand winning Short to long_still outline."""

from __future__ import annotations

import argparse

from rich.console import Console

from shorts_bot.config import settings
from shorts_bot.memory.store import MemoryStore
from shorts_bot.production.script_expand import expand_short_to_long_outline, write_long_outline

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(description="Expand Short script to long-form outline")
    parser.add_argument("--draft-id", type=int, required=True)
    parser.add_argument("--target-words", type=int, default=1000)
    parser.add_argument(
        "--output-dir",
        type=str,
        default="",
        help="Pack dir (default: draft_N_long_still under production)",
    )
    args = parser.parse_args()

    store = MemoryStore(settings.database_path)
    draft = store.get_draft(args.draft_id)
    if args.output_dir:
        pack_dir = settings.data_dir / "production" / args.output_dir
    else:
        pack_dir = settings.data_dir / "production" / f"draft_{args.draft_id}_long_still"

    outline = expand_short_to_long_outline(
        draft_id=args.draft_id,
        topic=draft.topic,
        hook=draft.hook,
        script=draft.script,
        target_words=args.target_words,
    )
    path = write_long_outline(pack_dir, outline)
    console.print(f"[green]{outline.message}[/green]")
    console.print(f"[dim]Wrote {path}[/dim]")


if __name__ == "__main__":
    main()
