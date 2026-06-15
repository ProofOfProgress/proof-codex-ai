"""CLI — Blender render self-reinforcement (try params → score → learn)."""

from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console

from shorts_bot.config import settings
from shorts_bot.production.blender.self_train import run_blender_self_train

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Blender self-train — render trials scored by vision QC; best params saved"
    )
    parser.add_argument("--draft-id", type=int, default=2)
    parser.add_argument("--pack-dir", type=Path, default=None)
    parser.add_argument("--trials", type=int, default=None, help="Override BLENDER_SELF_TRAIN_TRIALS")
    parser.add_argument("--target-score", type=float, default=None, help="Stop early when reached")
    parser.add_argument("--topic", default="micro jumpscare lunge")
    args = parser.parse_args()

    if not settings.blender_self_train_enabled:
        console.print("[yellow]BLENDER_SELF_TRAIN_ENABLED=false — exiting[/yellow]")
        raise SystemExit(0)

    result = run_blender_self_train(
        args.draft_id,
        pack_dir=args.pack_dir,
        trials=args.trials,
        target_score=args.target_score,
        topic=args.topic,
    )
    console.print(f"[green]{result.message}[/green]")
    console.print(
        f"Preview: http://127.0.0.1:{settings.web_port}/preview/draft/{args.draft_id}?file=final_short.mp4"
    )


if __name__ == "__main__":
    main()
