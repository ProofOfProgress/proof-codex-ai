"""CLI — Module 4 Gemini sample image (9:16) for Kling."""

from __future__ import annotations

import argparse
import json

from rich.console import Console

console = Console()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Module 4 Gemini 9:16 sample image")
    sub = parser.add_subparsers(dest="cmd", required=True)

    gen = sub.add_parser("sample", help="Generate 9:16 staged sample from listing product photo")
    gen.add_argument("--product", required=True)
    gen.add_argument("--source", required=True, help="Listing/isolated product photo")
    gen.add_argument("--reference", default="", help="Optional in-context reference for scale")
    gen.add_argument("--style", default="auto", choices=["auto", "studio", "vanity", "lifestyle", "kitchen"])
    gen.add_argument("--out", default="", help="Output path (default data/tiktok_shop/samples/PRODUCT_916.jpg)")
    gen.add_argument("--force", action="store_true")
    gen.add_argument("--json", action="store_true")

    show = sub.add_parser("show-prompt", help="Print Gemini sample prompt without calling API")
    show.add_argument("--product", required=True)
    show.add_argument("--style", default="auto")
    show.add_argument("--reference", action="store_true")

    args = parser.parse_args(argv)

    if args.cmd == "show-prompt":
        from shorts_bot.tiktok_shop.module4_sample import build_sample_prompt

        console.print(build_sample_prompt(product_name=args.product, style=args.style, reference_note=args.reference))
        return

    if args.cmd == "sample":
        from pathlib import Path

        from shorts_bot.tiktok_shop.module4_sample import generate_module4_sample, sample_image_path

        out = Path(args.out) if args.out else None
        ref = Path(args.reference) if args.reference else None
        try:
            result = generate_module4_sample(
                product_name=args.product,
                source_image=Path(args.source),
                reference_image=ref,
                style=args.style,
                out_path=out,
                force=args.force,
            )
        except RuntimeError as exc:
            console.print(f"[red]{exc}[/red]")
            raise SystemExit(1) from exc

        if args.json:
            payload = {
                "product": result.product_name,
                "source_image": result.source_image,
                "sample_path": str(result.sample_path.resolve()),
                "size": f"{result.width}x{result.height}",
                "model": result.model,
                "default_kling_input": str(result.sample_path.resolve()),
            }
            console.print_json(json.dumps(payload))
        else:
            console.print(f"[green]Sample[/green] {result.sample_path} ({result.width}x{result.height})")
            console.print(f"[dim]Model: {result.model}[/dim]")
            console.print(
                "[dim]Next: prompt-dispatch + save-prompt → render with "
                f"--image {result.sample_path}[/dim]"
            )
            default = sample_image_path(args.product)
            if result.sample_path != default:
                console.print(f"[dim]Default path: {default}[/dim]")
        return


if __name__ == "__main__":
    main()
