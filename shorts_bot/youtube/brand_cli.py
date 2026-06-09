from __future__ import annotations

import argparse

from rich.console import Console
from rich.panel import Panel

from shorts_bot.config import settings
from shorts_bot.youtube.channel_branding import YouTubeChannelBranding

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Apply channel display name and description in YouTube Studio."
    )
    parser.add_argument(
        "--channel-name",
        help="Override display name (default: channel/brand/youtube_copy.txt).",
    )
    parser.add_argument(
        "--description",
        help="Override description text.",
    )
    parser.add_argument(
        "--no-brand-file",
        action="store_true",
        help="Do not read youtube_copy.txt; require --channel-name and/or --description.",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser headless (not recommended for first login).",
    )
    args = parser.parse_args()

    console.print(
        Panel(
            "[bold]Apply Channel Branding[/bold]\n\n"
            "Opens YouTube Studio with your saved browser session and updates "
            "display name + description.\n"
            "[yellow]You must be logged into YouTube once in this profile.[/yellow]",
            border_style="blue",
        )
    )

    operator = YouTubeChannelBranding(
        profile_dir=settings.browser_profile_dir,
        headless=args.headless,
    )
    if args.no_brand_file:
        result = operator.apply(channel_name=args.channel_name, description=args.description)
    elif args.channel_name or args.description:
        result = operator.apply(channel_name=args.channel_name, description=args.description)
    else:
        result = operator.apply_from_brand_file()

    style = "green" if result.status in {"applied", "partial"} else "yellow"
    console.print(Panel(result.for_human(), title=result.status, border_style=style))


if __name__ == "__main__":
    main()
