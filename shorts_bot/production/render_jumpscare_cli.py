"""Regenerate only the dedicated Hailuo jumpscare clip for a draft pack."""

from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console

from shorts_bot.config import settings
from shorts_bot.production.jumpscare_clip import render_dedicated_jumpscare_clip
from shorts_bot.production.render_video import render_short_video

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render dedicated Hailuo jumpscare clip + optional full re-render"
    )
    parser.add_argument("--draft-id", type=int, required=True)
    parser.add_argument("--pack-dir", type=Path, default=None)
    parser.add_argument("--force", action="store_true", help="Regenerate I2V even if clip exists")
    parser.add_argument("--render", action="store_true", help="Also rebuild final_short.mp4")
    args = parser.parse_args()

    pack_dir = args.pack_dir or (settings.data_dir / "production" / f"draft_{args.draft_id}")
    console.print(f"[cyan]Generating dedicated jumpscare I2V for draft #{args.draft_id}…[/cyan]")
    if args.force:
        from shorts_bot.production.ai_video_guard import require_ai_video_generation

        require_ai_video_generation(action="render_jumpscare_cli --force")
    out = render_dedicated_jumpscare_clip(pack_dir, force=args.force)
    console.print(f"[green]Jumpscare clip ready: {out}[/green]")

    if args.render:
        rendered = render_short_video(pack_dir, draft_id=args.draft_id)
        console.print(f"[green]{rendered.message}[/green]")


if __name__ == "__main__":
    main()
