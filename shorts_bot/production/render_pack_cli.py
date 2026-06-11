"""Assemble final_short.mp4 from existing clips — no Replicate I2V."""

from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console

from shorts_bot.config import settings
from shorts_bot.production.render_video import render_short_video

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render final Short from cached clips/stills (no AI video generation)"
    )
    parser.add_argument("--draft-id", type=int, required=True)
    parser.add_argument("--pack-dir", type=Path, default=None)
    parser.add_argument(
        "--output-name",
        default="final_short.mp4",
        help="Output filename inside pack dir",
    )
    args = parser.parse_args()

    pack = args.pack_dir or (settings.data_dir / "production" / f"draft_{args.draft_id}")
    console.print(
        f"[cyan]Render-only draft #{args.draft_id} — assembling from {pack}/clips (no Replicate)[/cyan]"
    )
    result = render_short_video(
        pack,
        draft_id=args.draft_id,
        output_name=args.output_name,
    )
    console.print(f"[green]{result.message}[/green]")


if __name__ == "__main__":
    main()
