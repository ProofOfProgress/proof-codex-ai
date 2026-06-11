"""CLI — export AI video prompts into a production pack folder."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rich.console import Console

from shorts_bot.config import settings
from shorts_bot.production.video_prompt_pack import export_from_manifest

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(description="Export AI video prompts into a draft pack.")
    parser.add_argument("--draft-id", type=int, required=True, help="Draft ID (e.g. 9)")
    parser.add_argument(
        "--hybrid",
        action="store_true",
        help="Mark clip 1 as AI video hero (FLUX → I2V → hard cut to stick)",
    )
    parser.add_argument(
        "--no-hybrid",
        action="store_true",
        help="Export prompts only — no hero flag",
    )
    args = parser.parse_args()

    pack_dir = settings.data_dir / "production" / f"draft_{args.draft_id}"
    if not pack_dir.exists():
        console.print(f"[red]Pack not found: {pack_dir}[/red]")
        raise SystemExit(1)

    hybrid: bool | None = True if args.hybrid else (False if args.no_hybrid else None)
    payload = export_from_manifest(pack_dir, hybrid_hook=hybrid)
    console.print(f"[green]Exported {len(payload['clips'])} video prompts → {pack_dir}/video_prompts/[/green]")
    console.print(f"[dim]Hook template: {payload['hook_template_id']} ({payload['hook_model_hint']})[/dim]")
    console.print(f"[dim]Guide: {pack_dir / 'AI_VIDEO_HOOK.md'}[/dim]")
    if payload.get("hybrid_hook"):
        console.print("[cyan]Clip 1 flagged ai_video_hero — hybrid workflow[/cyan]")


if __name__ == "__main__":
    main()
