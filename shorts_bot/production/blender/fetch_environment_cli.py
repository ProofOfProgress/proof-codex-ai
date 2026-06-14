"""CLI: download Peripheral gas-station environment asset."""

from __future__ import annotations

import argparse

from rich.console import Console

from shorts_bot.production.blender.download_environment import ensure_gas_station_environment
from shorts_bot.production.blender.environment_paths import environment_model_status

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch CC0 gas-station environment for Blender")
    parser.add_argument("--force", action="store_true", help="Re-download and re-extract")
    parser.add_argument("--status", action="store_true", help="Print path resolution only")
    args = parser.parse_args()

    if args.status:
        status = environment_model_status()
        console.print(status)
        return

    path = ensure_gas_station_environment(force=args.force)
    console.print(f"[green]✓[/green] {path}")


if __name__ == "__main__":
    main()
