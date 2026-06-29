"""Prompt builder dispatch helpers — reference image paths for subagent."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rich.console import Console

from shorts_bot.tiktok_shop.pipeline import (
    dispatch_brief,
    load_prompt_file,
    prompt_path_for_product,
    save_prompt_file,
)

console = Console()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Product video prompt builder dispatch")
    sub = parser.add_subparsers(dest="cmd", required=True)

    brief = sub.add_parser("brief", help="Print CEO dispatch block for product-video-prompt-builder")
    brief.add_argument("--product", required=True)
    brief.add_argument("--product-image", required=True, help="Module 4 isolated/staged product image")
    brief.add_argument("--reference-image", default="", help="In-context reference for scale")
    brief.add_argument("--mission", default="")
    brief.add_argument("--handoff", default="", help="Visual critic handoff text file or inline")
    brief.add_argument("--json", action="store_true", help="JSON output for automation")

    save = sub.add_parser("save", help="Save prompt builder output to prompts/PRODUCT.kling.txt")
    save.add_argument("--product", required=True)
    save.add_argument("--prompt", default="", help="Prompt text inline")
    save.add_argument("--prompt-file", default="", help="Read prompt from file instead")

    show = sub.add_parser("show", help="Show saved prompt for product")
    show.add_argument("--product", required=True)

    args = parser.parse_args(argv)

    if args.cmd == "brief":
        handoff = args.handoff.strip()
        if handoff and Path(handoff).is_file():
            handoff = Path(handoff).read_text(encoding="utf-8")
        ref = Path(args.reference_image) if args.reference_image else None
        text = dispatch_brief(
            product_name=args.product,
            product_image=Path(args.product_image),
            reference_image=ref,
            mission_id=args.mission,
            visual_handoff=handoff,
        )
        if args.json:
            payload = {
                "agent": "product-video-prompt-builder",
                "product": args.product,
                "product_image": str(Path(args.product_image).resolve()),
                "reference_image": str(ref.resolve()) if ref and ref.is_file() else "",
                "brief": text,
            }
            console.print_json(json.dumps(payload))
        else:
            console.print(text)
        return

    if args.cmd == "save":
        prompt = (args.prompt or "").strip()
        if args.prompt_file:
            prompt = Path(args.prompt_file).read_text(encoding="utf-8").strip()
        if not prompt:
            console.print("[red]Provide --prompt or --prompt-file[/red]")
            raise SystemExit(1)
        path = save_prompt_file(product_name=args.product, prompt=prompt)
        console.print(f"[green]Saved[/green] {path}")
        return

    if args.cmd == "show":
        path = prompt_path_for_product(args.product)
        if not path.is_file():
            console.print(f"[red]No saved prompt:[/red] {path}")
            raise SystemExit(1)
        console.print(load_prompt_file(path))
        return


if __name__ == "__main__":
    main()
