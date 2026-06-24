"""CLI — Printify shop + product sync for seller clips."""

from __future__ import annotations

import json

from rich.console import Console
from rich.table import Table

console = Console()


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Printify API for TikTok Shop seller")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="Token + shop connectivity")
    sub.add_parser("shops", help="List Printify shops")
    sub.add_parser("sync", help="Cache products → data/tiktok_shop/printify_products.json")

    products = sub.add_parser("products", help="List products (from cache or live API)")
    products.add_argument("--live", action="store_true")

    show = sub.add_parser("show", help="Show one product")
    show.add_argument("--id", default="")
    show.add_argument("--title", default="")

    args = parser.parse_args()

    if args.cmd == "status":
        from shorts_bot.tiktok_shop import printify_client

        if not printify_client.configured():
            console.print("[red]Printify: not configured[/red]")
            console.print("Add PRINTIFY_API_TOKEN — see docs/FOR_OWNER_PRINTIFY_API.md")
            raise SystemExit(1)
        try:
            shops = printify_client.list_shops()
            sid = printify_client.resolve_shop_id()
        except RuntimeError as exc:
            console.print(f"[red]{exc}[/red]")
            raise SystemExit(1) from exc
        console.print("[green]Printify: configured[/green]")
        console.print(f"Shops: {len(shops)} | active shop_id: [cyan]{sid}[/cyan]")
        return

    if args.cmd == "shops":
        from shorts_bot.tiktok_shop import printify_client

        table = Table(title="Printify shops")
        table.add_column("ID")
        table.add_column("Title")
        table.add_column("Sales channel")
        for shop in printify_client.list_shops():
            table.add_row(
                str(shop.get("id") or ""),
                str(shop.get("title") or ""),
                str(shop.get("sales_channel") or ""),
            )
        console.print(table)
        return

    if args.cmd == "sync":
        from shorts_bot.tiktok_shop import printify_client

        path = printify_client.sync_products()
        rows = printify_client.load_cached_products()
        console.print(f"[green]Synced {len(rows)} products[/green] → {path}")
        return

    if args.cmd == "products":
        from shorts_bot.tiktok_shop import printify_client

        rows = (
            printify_client.list_products(limit=50)
            if args.live
            else printify_client.load_cached_products()
        )
        if not rows and not args.live:
            console.print("[yellow]Cache empty — run: printify_cli sync[/yellow]")
            return
        table = Table(title="Printify products")
        table.add_column("ID")
        table.add_column("Title")
        table.add_column("Hero image")
        for row in rows[:30]:
            if "printify_id" in row:
                pid = row.get("printify_id")
                title = row.get("title")
                hero = (row.get("hero_image") or "")[:40]
            else:
                pid = row.get("id")
                title = row.get("title")
                hero = (printify_client.hero_image_url(row) or "")[:40]
            table.add_row(str(pid), str(title or "")[:50], hero or "—")
        console.print(table)
        return

    if args.cmd == "show":
        from shorts_bot.tiktok_shop import printify_client

        row = printify_client.find_product(product_id=args.id, title=args.title)
        console.print(json.dumps(
            {
                "id": row.get("id"),
                "title": row.get("title"),
                "visible": row.get("visible"),
                "hero_image": printify_client.hero_image_url(row),
                "tags": row.get("tags"),
            },
            indent=2,
        ))
        return


if __name__ == "__main__":
    main()
