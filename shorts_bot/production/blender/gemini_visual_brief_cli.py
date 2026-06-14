"""Send LIGHTS ARE OFF reference links to Gemini → save visual brief for agents."""

from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console

from shorts_bot.config import settings
from shorts_bot.production.blender.gemini_blender_reference import (
    LIGHTS_ARE_OFF_URLS,
    ask_gemini_blender_brief,
)

console = Console()
DEFAULT_OUT = settings.data_dir / "research" / "PERIPHERAL_BLENDER_QUALITY_BRIEF.md"


def main() -> None:
    parser = argparse.ArgumentParser(description="Gemini brief from LIGHTS ARE OFF references")
    parser.add_argument(
        "--scene",
        default="Draft #2 — rural gas station at night, Form 2 creature, 3×10s EEVEE clips",
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--print-only", action="store_true")
    args = parser.parse_args()

    console.print("[cyan]Reference URLs sent to Gemini:[/cyan]")
    for url in LIGHTS_ARE_OFF_URLS:
        console.print(f"  {url}")

    brief = ask_gemini_blender_brief(scene=args.scene)
    header = (
        "# Peripheral Blender quality brief (Gemini + LIGHTS ARE OFF refs)\n\n"
        "Reference links included in prompt:\n"
        + "\n".join(f"- {u}" for u in LIGHTS_ARE_OFF_URLS)
        + "\n\n---\n\n"
    )
    body = header + brief
    if args.print_only:
        console.print(body)
        return
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(body, encoding="utf-8")
    console.print(f"[green]Saved[/green] {args.out}")


if __name__ == "__main__":
    main()
