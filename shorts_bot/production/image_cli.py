"""Test paid image generator — one frame from prompt."""

from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console

from shorts_bot.config import settings
from shorts_bot.production.caption_overlay import apply_bottom_caption
from shorts_bot.production.images.router import generate_image

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate one test image via Replicate/Fal.")
    parser.add_argument(
        "--prompt",
        default=(
            "Calm faceless bedroom at 3am, phone face-down on nightstand, soft moonlight, "
            "deep navy and mist blue tones, minimal, vertical 9:16 still, no text, no faces."
        ),
    )
    parser.add_argument("--caption", default="I used to grab my phone at 3am.")
    parser.add_argument("--out", type=Path, default=Path("data/production/test_ai_frame.png"))
    args = parser.parse_args()

    if not settings.has_paid_images:
        console.print("[red]Set RECRAFT_API_KEY, REPLICATE_API_TOKEN, or FAL_API_KEY in Cursor Secrets[/red]")
        raise SystemExit(1)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    from shorts_bot.production.captions import burn_captions_on_frames

    provider = generate_image(args.prompt, args.out)
    if burn_captions_on_frames():
        apply_bottom_caption(args.out, args.caption)
    else:
        console.print("[dim]caption_mode=ffmpeg — captions added at MP4 render, not on PNG[/dim]")
    console.print(f"[green]Saved {args.out} via {provider}[/green]")
    if (settings.image_provider or "").strip().lower() == "recraft":
        console.print(
            f"Recraft model: {settings.recraft_model} | style: {settings.recraft_style_id or '(none)'}"
        )
    else:
        console.print(f"Provider setting: {settings.image_provider} | model: {settings.replicate_image_model}")


if __name__ == "__main__":
    main()
