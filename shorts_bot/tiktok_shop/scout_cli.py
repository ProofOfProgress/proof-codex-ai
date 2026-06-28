"""CLI — EchoTik product scout for TikTok Shop."""

from __future__ import annotations

import argparse
import json

from rich.console import Console
from rich.table import Table

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(description="EchoTik TikTok Shop product scout")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="EchoTik credentials configured?")
    sub.add_parser("ping", help="Live API test (1 call — checks quota + latest data date)")

    run = sub.add_parser("run", help="Fetch + score products")
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
        from shorts_bot.config import settings
        from shorts_bot.tiktok_shop import echotik_client
        from shorts_bot.tiktok_shop.product_scout import load_products, products_path

        ok = echotik_client.configured()
        if ok:
            console.print("[green]EchoTik: configured[/green]")
        else:
            console.print("[red]EchoTik: not configured[/red]")
            console.print("See docs/FOR_OWNER_ECHOTIK_SETUP.md")
        console.print(f"Region: {settings.echotik_region or 'US'}")
        console.print(f"Products file: {products_path()}")
        console.print(f"Saved products: {len(load_products())}")
        if ok:
            console.print("[dim]Run: python3 -m shorts_bot.tiktok_shop.scout_cli ping[/dim]")
        return

    if args.cmd == "ping":
        from shorts_bot.tiktok_shop import echotik_client

        if not echotik_client.configured():
            console.print("[red]EchoTik not configured — see docs/FOR_OWNER_ECHOTIK_SETUP.md[/red]")
            raise SystemExit(1)
        try:
            result = echotik_client.ping()
        except RuntimeError as exc:
            console.print(f"[red]{exc}[/red]")
            raise SystemExit(1) from exc

        if not result.get("ok"):
            console.print(f"[red]EchoTik quota/error:[/red] {result.get('message')}")
            console.print("Upgrade plan at echotik.live or wait for quota reset.")
            raise SystemExit(1)

        console.print("[green]EchoTik API: connected[/green]")
        console.print(f"Region: {result.get('region')}")
        if result.get("rank_date"):
            console.print(f"Latest ranklist date: {result['rank_date']}")
            console.print(f"Sample: {result.get('sample_product')}")
            console.print(f"Sample GMV increment: {result.get('sample_gmv')}")
        else:
            console.print(f"[yellow]{result.get('message', 'No recent ranklist data')}[/yellow]")
        return

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
