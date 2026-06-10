"""CLI: generate profile + banner PNGs."""

from rich.console import Console

from shorts_bot.brand.assets import ensure_brand_assets

console = Console()


def main() -> None:
    profile, banner = ensure_brand_assets()
    console.print(f"[green]Profile:[/green] {profile}")
    console.print(f"[green]Banner:[/green] {banner}")


if __name__ == "__main__":
    main()
