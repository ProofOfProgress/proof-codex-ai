"""CLI: scaffold long_still production pack."""

from __future__ import annotations

import argparse

from rich.console import Console

from shorts_bot.config import settings
from shorts_bot.production.long_still_pack import scaffold_long_still_pack

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(description="Scaffold long_still pack (16:9 Ken Burns)")
    parser.add_argument("--draft-id", type=int, required=True)
    parser.add_argument("--beats", type=int, default=16)
    parser.add_argument(
        "--outline",
        type=str,
        default="",
        help="Path to long_script_outline.json (under production/)",
    )
    args = parser.parse_args()

    outline_path = None
    if args.outline:
        outline_path = settings.data_dir / "production" / args.outline

    result = scaffold_long_still_pack(
        draft_id=args.draft_id,
        outline_path=outline_path,
        target_beats=args.beats,
    )
    console.print(f"[green]{result.message}[/green]")


if __name__ == "__main__":
    main()
