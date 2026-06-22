"""Quote InVideo Generate credit cost before spending — no click."""

from __future__ import annotations

import argparse

from rich.console import Console

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(description="Read InVideo Generate credit cost (no render)")
    parser.add_argument("--url", required=True, help="InVideo project URL")
    parser.add_argument("--max-credits", type=int, default=10, help="Fail if cost exceeds this")
    args = parser.parse_args()

    from shorts_bot.invideo.credit_guard import quote_generate_credits

    cost = quote_generate_credits(args.url)
    if cost == 0:
        console.print("[green]Already rendered — Download available (0 credits to re-generate)[/green]")
        raise SystemExit(0)

    console.print(f"[bold]Generate cost: {cost} credits[/bold]")
    if cost > args.max_credits:
        console.print(
            f"[red]Over budget — max allowed {args.max_credits}. "
            "Switch to Basic + stock and rebuild brief.[/red]"
        )
        raise SystemExit(1)
    console.print(f"[green]Within budget (≤{args.max_credits})[/green]")


if __name__ == "__main__":
    main()
