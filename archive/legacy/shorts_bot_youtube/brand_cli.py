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
        help="Apply everything via Playwright Studio (skip API).",
    )
    args = parser.parse_args()

    console.print(
        Panel(
            "[bold]Apply Channel Branding (API)[/bold]\n\n"
            "Updates description + banner via API; display name via Studio browser fallback.\n"
            "(YouTube API cannot rename channels — Studio only.)\n"
            "Profile picture: Studio upload when browser profile is logged in.",
            border_style="blue",
        )
    )

    ops = BotOperations()
    if args.browser:
        from shorts_bot.brand.assets import ensure_brand_assets
        from shorts_bot.config import settings
        from shorts_bot.youtube.channel_branding import YouTubeChannelBranding

        ensure_brand_assets()
        operator = YouTubeChannelBranding(
            profile_dir=settings.browser_profile_dir,
            headless=True,
        )
        if args.channel_name or args.description:
            profile, banner = ensure_brand_assets()
            result_obj = operator.apply(
                channel_name=args.channel_name,
                description=args.description,
                profile_path=profile,
                banner_path=banner,
            )
        else:
            result_obj = operator.apply_from_brand_file()
        result = {
            "ok": result_obj.status in {"applied", "partial"},
            "status": result_obj.status,
            "message": result_obj.for_human(),
        }
    else:
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
