from __future__ import annotations

import argparse

from rich.console import Console
from rich.panel import Panel

from shorts_bot.config import settings
from shorts_bot.services.ops import BotOperations

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Apply channel name, description, and banner via YouTube API."
    )
    parser.add_argument("--channel-name", help="Override display name.")
    parser.add_argument("--description", help="Override description.")
    parser.add_argument(
        "--browser",
        action="store_true",
        help="Fallback to Playwright Studio automation (legacy).",
    )
    args = parser.parse_args()

    console.print(
        Panel(
            "[bold]Apply Channel Branding (API)[/bold]\n\n"
            "Updates name + description + banner without opening a browser.\n"
            "Profile picture: upload channel/brand/assets/profile.png manually in Studio.",
            border_style="blue",
        )
    )

    ops = BotOperations()
    result = ops.apply_channel_branding(
        channel_name=args.channel_name,
        description=args.description,
        use_brand_file=not (args.channel_name or args.description),
        use_browser_fallback=args.browser,
    )
    style = "green" if result.get("ok") else "yellow"
    console.print(Panel(result.get("message", "Done"), title=result.get("status", "done"), border_style=style))


if __name__ == "__main__":
    main()
