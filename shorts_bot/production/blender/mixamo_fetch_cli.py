"""Fetch Mixamo FBX motion clips for a draft (cloud motion → Blender render)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rich.console import Console

from shorts_bot.config import settings
from shorts_bot.production.blender.creature_paths import resolve_creature_model
from shorts_bot.production.blender.mixamo_client import fetch_draft_motions
from shorts_bot.production.blender.phase_motion_prompts import (
    ensure_draft_motion_json,
    export_motion_prompts_file,
    phase_queries_for_draft,
)

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(description="Mixamo → motion_exports FBX for Blender cloud render")
    parser.add_argument("--draft-id", type=int, default=2)
    parser.add_argument(
        "--model",
        type=Path,
        default=None,
        help="Creature FBX to upload (default: scp_096.fbx)",
    )
    parser.add_argument(
        "--login-wait",
        type=int,
        default=0,
        metavar="SEC",
        help="Open browser and wait up to SEC seconds for Adobe login (e.g. 900 = 15 min)",
    )
    parser.add_argument("--headed", action="store_true", help="Show browser window (for login)")
    parser.add_argument("--out-dir", type=Path, default=None)
    args = parser.parse_args()

    model = args.model
    if model is None:
        fbx = Path("channel/assets/creatures/scp_096/scp_096.fbx")
        model = fbx if fbx.is_file() else resolve_creature_model()
    if model is None:
        model = Path("channel/assets/creatures/scp_096/scp_096.fbx")
    if model.suffix.lower() not in (".fbx", ".obj", ".zip"):
        raise SystemExit(f"Mixamo needs FBX/OBJ/ZIP — got {model.suffix}. Use scp_096.fbx")
    out_dir = args.out_dir or (Path(__file__).resolve().parents[3] / "channel" / "assets" / "motion_exports")

    ensure_draft_motion_json(args.draft_id)
    queries = phase_queries_for_draft(args.draft_id)
    pack = settings.data_dir / "production" / f"draft_{args.draft_id}"
    prompt_doc = export_motion_prompts_file(args.draft_id, pack)

    if args.login_wait > 0:
        console.print(
            "[bold yellow]Mixamo login[/bold yellow] — browser opening.\n"
            "1. Click [cyan]Log In[/cyan] → sign in with Adobe (free account OK)\n"
            "2. Leave this running — automation continues after login\n"
        )

    console.print(f"Model: {model}")
    console.print(f"Output: {out_dir}")
    console.print(f"Mixamo searches: {queries}")
    console.print(f"Prompts doc: {prompt_doc}")

    results = fetch_draft_motions(
        draft_id=args.draft_id,
        model_path=model,
        out_dir=out_dir,
        login_wait_sec=args.login_wait,
        headless=False if args.headed or args.login_wait else None,
    )

    manifest = {
        "draft_id": args.draft_id,
        "source": "mixamo",
        "model": str(model),
        "prompts_file": str(pack / "motion_prompts.json"),
        "clips": [
            {
                "phase": r.phase,
                "query": r.query,
                "animation": r.animation_name,
                "path": str(r.output_path),
            }
            for r in results
        ],
    }
    manifest_path = out_dir / f"draft_{args.draft_id}_mixamo_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    console.print("[green]Downloaded Mixamo motion:[/green]")
    for r in results:
        console.print(f"  {r.phase}: {r.animation_name} → {r.output_path.name}")
    console.print(f"\nManifest: {manifest_path}")
    console.print(
        f"\nNext: cloud re-render draft #{args.draft_id} — "
        f"python3 -m shorts_bot.production.blender.produce_cli --draft-id {args.draft_id} --force"
    )


if __name__ == "__main__":
    main()
