"""CLI — FastMoss / product scout for TikTok Shop."""

from __future__ import annotations

import argparse
import json

from rich.console import Console
from rich.table import Table

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(description="TikTok Shop product scout (FastMoss)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="FastMoss / research credentials")
    sub.add_parser("ping", help="Live API test (FastMoss when configured)")

    run = sub.add_parser("run", help="Fetch + score products (FastMoss API when wired)")
    run.add_argument(
        "--preset",
        choices=("middle_core", "two_hundred"),
        default="middle_core",
    )
    run.add_argument("--limit", type=int, default=10)
    run.add_argument("--json", action="store_true")

    list_cmd = sub.add_parser("list", help="Show saved products.json")

    report = sub.add_parser("report", help="Plain-English report from saved products.json")
    report.add_argument("--preset", default="middle_core")

    args = parser.parse_args()

    if args.cmd == "status":
        from shorts_bot.tiktok_shop import echotik_client, fastmoss_client
        from shorts_bot.tiktok_shop.product_scout import load_products, products_path

        if fastmoss_client.configured():
            console.print("[green]FastMoss: credentials configured[/green]")
            console.print("[yellow]Automated scout: not wired yet — use FastMoss app or see FASTMOSS_SCOUT_PLAN.md[/yellow]")
        else:
            console.print("[red]FastMoss: not configured[/red]")
            console.print("See docs/FOR_OWNER_FASTMOSS_SETUP.md (replaces EchoTik)")
        if echotik_client.configured():
            console.print("[dim]EchoTik: legacy credentials present — retired, do not pay[/dim]")
        console.print(f"Products file: {products_path()}")
        console.print(f"Saved products: {len(load_products())}")
        console.print("[dim]Launch path A: pick in FastMoss app → tell agent product names[/dim]")
        return

    if args.cmd == "ping":
        from shorts_bot.tiktok_shop import fastmoss_client, echotik_client

        if fastmoss_client.configured():
            result = fastmoss_client.ping()
            if result.get("ok"):
                console.print("[green]FastMoss API: connected[/green]")
            else:
                console.print(f"[yellow]FastMoss:[/yellow] {result.get('message')}")
            return

        if echotik_client.configured():
            console.print("[yellow]EchoTik is retired — configure FastMoss instead[/yellow]")
            console.print("docs/FOR_OWNER_FASTMOSS_SETUP.md")
            raise SystemExit(1)

        console.print("[red]FastMoss not configured — docs/FOR_OWNER_FASTMOSS_SETUP.md[/red]")
        raise SystemExit(1)

    if args.cmd == "list":
        from shorts_bot.tiktok_shop.product_scout import load_products

        rows = load_products()
        if not rows:
            console.print("[yellow]No products yet — run scout run[/yellow]")
            return
        table = Table(title="Saved Shop products")
        table.add_column("Product")
        table.add_column("$/sale")
        table.add_column("GMV")
        table.add_column("Creators")
        for r in rows:
            table.add_row(
                (r.get("product_name") or "")[:40],
                f"${r.get('commission_usd', 0)}",
                f"${int(r.get('gmv_period', 0)):,}",
                str(r.get("creators", "")),
            )
        console.print(table)
        return

    if args.cmd == "report":
        from shorts_bot.tiktok_shop.product_scout import load_products
        from shorts_bot.tiktok_shop.scout_report import format_scout_report

        console.print(format_scout_report(load_products(), preset=args.preset))
        return

    if args.cmd == "run":
        from shorts_bot.tiktok_shop.product_scout import save_products, scout_products

        try:
            products = scout_products(preset=args.preset, limit=args.limit)
        except RuntimeError as exc:
            console.print(f"[red]{exc}[/red]")
            raise SystemExit(1) from exc

        path = save_products(products)
        if args.json:
            console.print_json(json.dumps([p.to_dict() for p in products]))
            return

        if not products:
            console.print("[yellow]No products passed filters — try other preset or loosen rules[/yellow]")
            return

        table = Table(title=f"Scout results ({args.preset}) → {path}")
        table.add_column("Score")
        table.add_column("Product")
        table.add_column("Comm/sale")
        table.add_column("Creators")
        table.add_column("Videos")
        for p in products:
            table.add_row(
                f"{p.score:.0f}",
                p.product_name[:45],
                f"${p.commission_usd}",
                str(p.creators),
                str(p.videos),
            )
        console.print(table)
        console.print("[dim]Next: Kling clip → factory_cli enqueue → post-batch[/dim]")
        return


if __name__ == "__main__":
    main()
