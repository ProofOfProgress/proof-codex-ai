#!/usr/bin/env python3
"""Generate + QC + post bubble wrap carousels for multiple accounts."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Allow running as script from repo root
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from rich.console import Console

from shorts_bot.tiktok_shop.accounts import load_accounts
from shorts_bot.tiktok_shop.bubble_wrap_gen import generate_bubble_pair, qc_bubble_slide
from shorts_bot.tiktok_shop.bubble_wrap_post import post_bubble_wrap_carousel

console = Console()

PACKS = [
    {
        "slug": "playstation_duck",
        "account_id": "bubble_playstation",
        "subject": "cute yellow rubber duck",
        "hook_text": "DUCK BUBBLE WRAP ASMR >>>",
        "title": "Duck bubble wrap ASMR",
    },
    {
        "slug": "proof_frog",
        "account_id": "bubble_proof",
        "subject": "small green tree frog",
        "hook_text": "FROG BUBBLE WRAP ASMR >>>",
        "title": "Frog bubble wrap ASMR",
    },
    {
        "slug": "msbyte_cake",
        "account_id": "bubble_msbyte",
        "subject": "slice of chocolate layer cake",
        "hook_text": "CAKE BUBBLE WRAP ASMR >>>",
        "title": "Cake bubble wrap ASMR",
    },
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--confirm", action="store_true", help="Upload after QC")
    parser.add_argument("--skip-gen", action="store_true", help="Use existing PNGs only")
    args = parser.parse_args()

    accounts = {a.id: a for a in load_accounts()}
    failures = 0

    for pack in PACKS:
        slug = pack["slug"]
        account = accounts.get(pack["account_id"])
        if not account:
            console.print(f"[red]Missing account {pack['account_id']}[/red]")
            failures += 1
            continue

        console.print(f"\n[bold]=== {account.label} — {slug} ===[/bold]")

        if not args.skip_gen:
            console.print("Generating slides...")
            try:
                hook, cta = generate_bubble_pair(
                    slug=slug,
                    subject=pack["subject"],
                    hook_text=pack["hook_text"],
                )
            except Exception as exc:
                console.print(f"[red]Generate failed: {exc}[/red]")
                failures += 1
                continue
        else:
            from shorts_bot.config import settings

            base = settings.data_dir / "tiktok_shop" / "bubble_wrap" / slug
            hook = base / "slide1_hook.png"
            cta = base / "slide2_cta.png"

        pack_ok = True
        for path, role in ((hook, "hook"), (cta, "cta")):
            report = qc_bubble_slide(path, title=pack["title"], slide_role=role)
            console.print(f"QC {path.name}: {report.summary()}")
            if not report.passed:
                pack_ok = False
                failures += 1

        if not pack_ok:
            continue

        if not args.confirm:
            console.print("[yellow]Dry run — add --confirm to post[/yellow]")
            continue

        ok, msg, post_id = post_bubble_wrap_carousel(
            account,
            slide1=hook,
            slide2=cta,
            title=pack["title"],
        )
        if ok:
            console.print(f"[green]{msg}[/green] post_id={post_id}")
            time.sleep(2)
        else:
            console.print(f"[red]{msg}[/red]")
            failures += 1

    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
