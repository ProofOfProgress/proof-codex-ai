"""CLI — set Discord bot profile picture."""

from __future__ import annotations

import argparse

from rich.console import Console

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(description="Set Discord bot avatar (Inside Job president default).")
    parser.add_argument(
        "--image",
        default=None,
        help="Path to PNG/JPG (default: channel/brand/assets/discord_bot_avatar.png)",
    )
    args = parser.parse_args()

    from shorts_bot.discord_bot.avatar import set_bot_avatar_sync

    msg = set_bot_avatar_sync(path=args.image)
    console.print(f"[green]{msg}[/green]")


if __name__ == "__main__":
    main()
