"""CLI — peak still preflight gate (cheap QC before full Blender render)."""

from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console

from shorts_bot.config import settings
from shorts_bot.production.blender.preflight import run_preflight_gate

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(description="Render peak still + vision QC (no full clip)")
    parser.add_argument("--draft-id", type=int, default=2)
    parser.add_argument("--pack-dir", type=Path, default=None)
    parser.add_argument("--seconds", type=float, default=None)
    parser.add_argument("--samples", type=int, default=None)
    parser.add_argument("--topic", default="micro jumpscare lunge")
    parser.add_argument("--hook", default="creature lunge face fill")
    args = parser.parse_args()

    pack = args.pack_dir or (settings.data_dir / "production" / f"draft_{args.draft_id}")
    result = run_preflight_gate(
        args.draft_id,
        pack,
        seconds=args.seconds,
        samples=args.samples,
        topic=args.topic,
        hook=args.hook,
        force_still=True,
    )
    console.print(result.message)
    if result.still_path.is_file():
        console.print(f"Still: {result.still_path}")
    raise SystemExit(0 if result.passed else 1)


if __name__ == "__main__":
    main()
