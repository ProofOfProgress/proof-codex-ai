"""CLI — Gemini visual feedback for prompt ↔ render loop."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rich.console import Console

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gemini visual feedback — critique images/videos, suggest prompt revisions"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    img = sub.add_parser("review-image", help="Critique Module 4 still before Kling")
    img.add_argument("--image", required=True)
    img.add_argument("--product", default="")
    img.add_argument("--json", action="store_true")

    vid = sub.add_parser("review-video", help="Critique rendered clip + optional reference still")
    vid.add_argument("--video", required=True)
    vid.add_argument("--product", default="")
    vid.add_argument("--reference-image", default="", help="Module 4 product still")
    vid.add_argument("--prompt", default="", help="Kling prompt used for this render")
    vid.add_argument("--skip-module1", action="store_true")
    vid.add_argument("--json", action="store_true")

    sug = sub.add_parser("suggest-prompt", help="Rewrite Kling prompt from saved critique JSON")
    sug.add_argument("--critique", required=True, help="Path to visual_feedback/*.json")
    sug.add_argument("--prompt", default="", help="Original prompt text")
    sug.add_argument("--prompt-file", default="", help="File containing original prompt")
    sug.add_argument("--json", action="store_true")

    full = sub.add_parser(
        "review-and-suggest",
        help="Review video + auto-suggest revised prompt if not good enough",
    )
    full.add_argument("--video", required=True)
    full.add_argument("--product", default="")
    full.add_argument("--reference-image", default="")
    full.add_argument("--prompt", default="")
    full.add_argument("--json", action="store_true")

    handoff = sub.add_parser("handoff", help="Print paste block for product-video-prompt-builder")
    handoff.add_argument("--critique", required=True)

    args = parser.parse_args()

    from shorts_bot.tiktok_shop.visual_feedback import (
        VisualCritiqueReport,
        format_report_plain,
        review_and_suggest_prompt,
        review_reference_image,
        review_video,
        suggest_prompt_revision,
    )

    if args.cmd == "review-image":
        report = review_reference_image(Path(args.image), product=args.product)
        if args.json:
            console.print_json(json.dumps(report.to_dict()))
        else:
            console.print(format_report_plain(report))
        raise SystemExit(0 if report.good_enough else 1)

    if args.cmd == "review-video":
        ref = Path(args.reference_image) if args.reference_image else None
        report = review_video(
            Path(args.video),
            product=args.product,
            reference_image=ref,
            prompt_used=args.prompt,
            include_module1_qc=not args.skip_module1,
        )
        if args.json:
            console.print_json(json.dumps(report.to_dict()))
        else:
            console.print(format_report_plain(report))
        raise SystemExit(0 if report.good_enough else 1)

    if args.cmd == "suggest-prompt":
        data = json.loads(Path(args.critique).read_text(encoding="utf-8"))
        critique = VisualCritiqueReport(**{k: v for k, v in data.items() if k in VisualCritiqueReport.__dataclass_fields__})
        original = args.prompt
        if args.prompt_file:
            original = Path(args.prompt_file).read_text(encoding="utf-8").strip()
        if not original and critique.prompt_used:
            original = critique.prompt_used
        if not original:
            console.print("[red]Provide --prompt or --prompt-file[/red]")
            raise SystemExit(1)
        revised = suggest_prompt_revision(original_prompt=original, critique=critique, product=critique.product)
        if args.json:
            console.print_json(json.dumps({"revised_prompt": revised}))
        else:
            console.print(revised)
        return

    if args.cmd == "review-and-suggest":
        ref = Path(args.reference_image) if args.reference_image else None
        report = review_and_suggest_prompt(
            Path(args.video),
            product=args.product,
            reference_image=ref,
            prompt_used=args.prompt,
        )
        if args.json:
            console.print_json(json.dumps(report.to_dict()))
        else:
            console.print(format_report_plain(report))
            if report.revised_prompt:
                console.print("\n[dim]Paste handoff:[/dim] visual_feedback_cli handoff --critique ...")
        raise SystemExit(0 if report.good_enough else 1)

    if args.cmd == "handoff":
        data = json.loads(Path(args.critique).read_text(encoding="utf-8"))
        critique = VisualCritiqueReport(**{k: v for k, v in data.items() if k in VisualCritiqueReport.__dataclass_fields__})
        console.print(critique.handoff_for_prompt_builder())


if __name__ == "__main__":
    main()
