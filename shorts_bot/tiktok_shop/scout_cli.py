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
    run.add_argument("--preset", default="core_middle_core", help="Kalodata preset key (see kalodata_filters.json)")
    run.add_argument("--limit", type=int, default=10)
    run.add_argument("--json", action="store_true")

    list_cmd = sub.add_parser("list", help="Show saved products.json")

    sub.add_parser("validate", help="Quality-gate saved products.json (coach stats)")

    report = sub.add_parser("report", help="Plain-English report from saved products.json")
    report.add_argument("--preset", default="middle_core")

    args = parser.parse_args()

    if args.cmd == "status":
        from shorts_bot.tiktok_shop import fastmoss_client, kalodata_client, kalodata_filters
        from shorts_bot.tiktok_shop.product_scout import load_products, products_path
        from shorts_bot.tiktok_shop.scout_provider import resolve_scout_provider, scout_setup_hint

        provider = resolve_scout_provider(preset="middle_core")
        if provider == "hub_ui":
            console.print("[green]Scout backend: Kalodata hub UI (saved filter URLs)[/green]")
            console.print("[dim]Highest quality — course filters applied in Kalodata before URL copy[/dim]")
        elif provider == "kalodata":
            console.print("[green]Scout backend: Kalodata KaloPilot[/green]")
        elif provider == "fastmoss":
            console.print("[green]Scout backend: FastMoss OpenAPI (credentials set)[/green]")
            console.print("[yellow]Product rank endpoints not wired yet — token test via ping[/yellow]")
        elif provider == "momentum_weekly_drop":
            from shorts_bot.tiktok_shop.product_scout import load_momentum_weekly_drop

            n = len(load_momentum_weekly_drop(limit=50))
            console.print("[green]Scout backend: Momentum weekly drop (course intel)[/green]")
            console.print(f"[dim]{n} coach-vetted products in momentum_weekly_drop.json[/dim]")
        else:
            console.print("[red]Scout backend: not configured[/red]")
            console.print(scout_setup_hint(preset="middle_core"))

        missing = kalodata_filters.missing_presets()
        if missing:
            console.print(f"[yellow]Kalodata filter URLs missing:[/yellow] {', '.join(missing)}")
            console.print("[dim]Paste URLs in data/tiktok_shop/kalodata_filters.json — docs/FOR_OWNER_KALODATA_HUB_SETUP.md[/dim]")
        else:
            console.print("[green]All Kalodata filter URLs configured[/green]")

        if kalodata_client.configured():
            console.print("[dim]KaloPilot token: present (fallback)[/dim]")
        if fastmoss_client.configured():
            console.print("[dim]FastMoss API keys: present[/dim]")
        console.print(f"Products file: {products_path()}")
        console.print(f"Saved products: {len(load_products())}")
        return

    if args.cmd == "ping":
        from shorts_bot.tiktok_shop import fastmoss_client, kalodata_client, kalodata_filters
        from shorts_bot.tiktok_shop.scout_provider import resolve_scout_provider, scout_setup_hint

        provider = resolve_scout_provider(preset="middle_core")
        if provider == "hub_ui":
            url = kalodata_filters.preset_filter_url("middle_core")
            console.print("[green]Kalodata hub UI: filter URL configured[/green]")
            console.print(f"[dim]{url[:100]}...[/dim]" if len(url) > 100 else f"[dim]{url}[/dim]")
            console.print("[dim]Run scout on hub: bash scripts/scout_on_hub.sh run --preset middle_core[/dim]")
            return
        if provider == "kalodata":
            result = kalodata_client.ping()
            if result.get("ok"):
                console.print("[green]Kalodata KaloPilot: OK[/green]")
                if result.get("sample"):
                    console.print(f"[dim]{result['sample']}[/dim]")
            else:
                console.print(f"[red]Kalodata:[/red] {result.get('message')}")
                raise SystemExit(1)
            return
        if provider == "fastmoss":
            result = fastmoss_client.ping()
            if result.get("ok"):
                console.print("[green]FastMoss API: connected[/green]")
            else:
                console.print(f"[yellow]FastMoss:[/yellow] {result.get('message')}")
            return

        console.print(f"[red]{scout_setup_hint()}[/red]")
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

    if args.cmd == "validate":
        from shorts_bot.tiktok_shop.product_scout import ScoutProduct, load_products
        from shorts_bot.tiktok_shop.scout_product_quality import (
            filter_quality_products,
            format_quality_report,
            validate_product,
        )

        raw = load_products()
        if not raw:
            console.print("[yellow]No products in products.json[/yellow]")
            raise SystemExit(2)
        products = [ScoutProduct(**{**r, "product_id": r.get("product_id") or ""}) for r in raw]
        passed, rejected = filter_quality_products(products, limit=20, strict=True)
        console.print(format_quality_report(passed, rejected))
        if not passed:
            console.print("[red]ZERO products pass coach quality gate — do not use for launch[/red]")
            raise SystemExit(2)
        console.print(f"[green]{len(passed)} pass[/green] · [red]{len(rejected)} rejected[/red]")
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
