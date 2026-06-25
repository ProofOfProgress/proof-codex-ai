"""Generate Ms. Byte profile + cover PNGs for Facebook and TikTok."""

from __future__ import annotations

import argparse

from rich.console import Console

from shorts_bot.brand.assets import ensure_ms_byte_social_assets

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(description="Ms. Byte social profile + cover PNGs")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    paths = ensure_ms_byte_social_assets(force=args.force)
    for label, path in paths.items():
        console.print(f"[green]{label}:[/green] {path}")


if __name__ == "__main__":
    main()
