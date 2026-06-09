from __future__ import annotations

import argparse

from rich.console import Console
from rich.panel import Panel

from shorts_bot.config import settings
from shorts_bot.youtube.channel_setup import YouTubeChannelSetup

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Set up a YouTube channel via browser automation (Playwright)."
    )
    parser.add_argument(
        "--channel-name",
        default=settings.youtube_channel_name,
        help="Display name for the YouTube channel.",
    )
    parser.add_argument(
        "--existing-account",
        action="store_true",
        help="Skip new Google sign-up; use saved browser session or sign in manually.",
    )
    parser.add_argument(
        "--wait",
        type=int,
        default=0,
        help="Seconds to wait for human to finish phone/CAPTCHA verification.",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser headless (not recommended for sign-up).",
    )
    args = parser.parse_args()

    if not args.channel_name:
        console.print("[red]Channel name required.[/red] Use --channel-name 'Your Channel'")
        return

    console.print(
        Panel(
            "[bold]YouTube Channel Setup[/bold]\n\n"
            "The bot opens a real browser and does everything Google allows.\n"
            "[yellow]Google will ask for phone/CAPTCHA once — you must complete that step.[/yellow]\n"
            "After that, the session is saved and the bot reuses it.",
            border_style="blue",
        )
    )

    operator = YouTubeChannelSetup(
        profile_dir=settings.browser_profile_dir,
        headless=args.headless,
    )
    result = operator.run(
        channel_name=args.channel_name,
        use_existing_google_account=args.existing_account,
        wait_for_human_seconds=args.wait,
    )
    console.print(Panel(result.for_human(), title=result.status, border_style="green"))


if __name__ == "__main__":
    main()
