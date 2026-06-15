"""Recraft API setup — status checks + optional browser handoff."""

from __future__ import annotations

import argparse
import time

from rich.console import Console
from rich.table import Table

console = Console()

RECRAFT_PROFILE_URL = "https://recraft.ai/profile"
RECRAFT_PRICING_URL = "https://www.recraft.ai/docs/api-reference/pricing"
RECRAFT_STUDIO_URL = "https://app.recraft.ai"


def recraft_setup_status() -> tuple[bool, list[str]]:
    from shorts_bot.config import settings
    from shorts_bot.production.images.recraft import probe_recraft

    lines: list[str] = []
    ok = True
    provider = (settings.image_provider or "replicate").strip().lower()

    def check(name: str, passed: bool, detail: str) -> None:
        nonlocal ok
        if not passed:
            ok = False
        lines.append(f"{'OK' if passed else 'FIX'} {name}: {detail}")

    check(
        "Image provider",
        provider == "recraft",
        f"IMAGE_PROVIDER={provider!r} (want recraft)",
    )
    check(
        "Recraft API key",
        settings.has_recraft_images,
        "RECRAFT_API_KEY in Cursor Secrets → bash scripts/install.sh",
    )
    style_id = (settings.recraft_style_id or "").strip()
    check(
        "Custom style ID",
        bool(style_id),
        settings.recraft_style_id or "RECRAFT_STYLE_ID — copy from Recraft Studio (⋯ on your style)",
    )
    check(
        "Model for custom style",
        (settings.recraft_model or "").strip().lower().startswith("recraftv3"),
        f"RECRAFT_MODEL={settings.recraft_model!r} (custom styles need recraftv3)",
    )

    if settings.has_recraft_images:
        reachable, msg = probe_recraft(settings.recraft_api_key or "")
        check("Recraft API", reachable, msg)
    else:
        check("Recraft API", False, "add RECRAFT_API_KEY first")

    lines.append(
        f"Plan: {settings.recraft_model} @ {settings.recraft_image_size} "
        f"(~40 API units per still on V3)"
    )
    return ok, lines


def open_recraft_browser(*, wait_minutes: int = 20) -> None:
    from playwright.sync_api import sync_playwright

    from shorts_bot.browser.stealth import launch_stealth_context

    console.print(
        "[bold green]Opening Recraft in your Desktop browser…[/bold green]\n"
        "[yellow]In Cursor: click the Desktop tab.[/yellow]\n\n"
        "[bold]Do these in order:[/bold]\n"
        "1. Sign in (same account as your $100 annual Basic).\n"
        "2. Tab 1 — Profile: buy [cyan]API units[/cyan] if balance is 0 "
        "(web credits ≠ API units; ~$1 per 1,000 units).\n"
        "3. Tab 1 — click [cyan]Generate[/cyan] to create your API key → copy it.\n"
        "4. Tab 2 — Studio: open your funny-character [cyan]custom style[/cyan] → "
        "⋯ menu → Copy style ID.\n"
        "5. Paste both into Cursor Secrets as RECRAFT_API_KEY and RECRAFT_STYLE_ID.\n"
        "6. Set IMAGE_PROVIDER=recraft, CAPTION_MODE=off, BURN_IN_SUBTITLES=false.\n"
        "7. Run: [cyan]bash scripts/install.sh && python3 -m shorts_bot.production.recraft_setup_cli[/cyan]\n"
        f"\nWindow stays open {wait_minutes} minutes.\n"
    )

    urls = [
        (RECRAFT_PROFILE_URL, "Profile — API key + API units"),
        (RECRAFT_STUDIO_URL, "Studio — copy custom style ID"),
        (RECRAFT_PRICING_URL, "API pricing reference"),
    ]

    with sync_playwright() as p:
        context = launch_stealth_context(p, headless=False)
        page = context.pages[0] if context.pages else context.new_page()
        for i, (url, label) in enumerate(urls):
            if i == 0:
                page.goto(url, wait_until="domcontentloaded", timeout=120000)
            else:
                new_page = context.new_page()
                new_page.goto(url, wait_until="domcontentloaded", timeout=120000)
            console.print(f"[cyan]Tab {i + 1} ({label}):[/cyan] {url}")
        console.print("[bold]Complete the steps above, then leave this running.[/bold]")
        time.sleep(wait_minutes * 60)
        context.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify Recraft is ready for PERIPHERAL stills")
    parser.add_argument("--json", action="store_true", help="Machine-readable output")
    parser.add_argument(
        "--open-browser",
        action="store_true",
        help="Open Recraft profile + studio in Desktop browser for owner setup",
    )
    parser.add_argument("--minutes", type=int, default=20, help="Browser stay-open time")
    args = parser.parse_args()

    if args.open_browser:
        open_recraft_browser(wait_minutes=args.minutes)
        raise SystemExit(0)

    ready, lines = recraft_setup_status()

    if args.json:
        import json

        print(json.dumps({"ready": ready, "checks": lines}, indent=2))
        raise SystemExit(0 if ready else 1)

    table = Table(title="Recraft setup")
    table.add_column("Status", style="bold")
    table.add_column("Detail")
    for line in lines:
        if line.startswith("OK "):
            table.add_row("[green]OK[/green]", line[3:])
        elif line.startswith("FIX "):
            table.add_row("[red]FIX[/red]", line[4:])
        else:
            table.add_row("", line)
    console.print(table)

    if ready:
        console.print(
            "\n[green]Ready.[/green] Test one frame:\n"
            '  python3 -m shorts_bot.production.image_cli --prompt "funny crayon horror character in dark apartment, 9:16, no text"'
        )
    else:
        console.print(
            "\n[yellow]Not ready yet.[/yellow] Run with --open-browser to open Recraft:\n"
            "  python3 -m shorts_bot.production.recraft_setup_cli --open-browser"
        )
    raise SystemExit(0 if ready else 1)


if __name__ == "__main__":
    main()
