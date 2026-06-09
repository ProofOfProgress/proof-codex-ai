from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from shorts_bot.config import settings
from shorts_bot.memory.store import MemoryStore
from shorts_bot.production.pack import build_production_pack

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build timestamped still-image production pack from TurboScribe transcript."
    )
    parser.add_argument("--draft-id", type=int, required=True, help="Approved or pending draft ID")
    parser.add_argument(
        "--transcript",
        type=Path,
        help="TurboScribe export file (.txt). If omitted, reads stdin.",
    )
    args = parser.parse_args()

    if args.transcript:
        text = args.transcript.read_text(encoding="utf-8")
    else:
        console.print("[yellow]Paste TurboScribe transcript, then Ctrl+D:[/yellow]")
        import sys

        text = sys.stdin.read()

    store = MemoryStore(settings.database_path)
    try:
        pack = build_production_pack(store, draft_id=args.draft_id, turboscribe_text=text)
    except (ValueError, KeyError) as exc:
        console.print(f"[red]{exc}[/red]")
        raise SystemExit(1) from exc

    console.print(
        Panel(
            f"{pack.message}\n\nImages to generate: {pack.image_count}\nPath: {pack.output_dir}",
            title="Production pack",
            border_style="green",
        )
    )


if __name__ == "__main__":
    main()
