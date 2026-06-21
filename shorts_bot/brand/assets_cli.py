"""CLI: generate profile + banner PNGs."""

import argparse

from rich.console import Console

from shorts_bot.brand.assets import ensure_brand_assets

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Rapid Tool Review channel PNGs")
    parser.add_argument("--force", action="store_true", help="Regenerate even if files exist")
    args = parser.parse_args()
    profile, banner = ensure_brand_assets(force=args.force)
    console.print(f"[green]Profile:[/green] {profile}")
    console.print(f"[green]Banner:[/green] {banner}")


if __name__ == "__main__":
    main()
