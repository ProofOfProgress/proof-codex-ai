"""CLI — create Meta app 'Peripheral Bot' and save Facebook Page API token."""

from __future__ import annotations

import argparse
import time

from rich.console import Console

console = Console()

PASSWORD_HINT = """
[bold yellow]On Desktop — one quick step[/bold yellow]

Meta needs your Facebook password to create the app.

1. Look at the Desktop browser window
2. Type your Facebook password in the popup
3. Click [bold]Submit[/bold]

This agent will wait up to 10 minutes, then finish the app + token automatically.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Create Meta app and wire Facebook Page token")
    parser.add_argument("--app-name", default="Peripheral Bot", help="Meta app display name")
    parser.add_argument("--page-name", default="Peripheral Horror", help="Facebook Page to post as")
    parser.add_argument("--password-wait", type=int, default=600, help="Seconds to wait for password")
    parser.add_argument("--token-only", action="store_true", help="Skip app create; scrape token only")
    args = parser.parse_args()

    import subprocess

    from shorts_bot.browser.profile_lock import clear_stale_profile_lock

    clear_stale_profile_lock()
    subprocess.run(
        ["pkill", "-9", "-f", "chrome.*browser_profile"],
        check=False,
        capture_output=True,
    )
    time.sleep(2)
    clear_stale_profile_lock()

    if not args.token_only:
        console.print("[bold]Step 1:[/bold] Create Meta app for Facebook autopost\n")
        console.print(PASSWORD_HINT)

    try:
        if args.token_only:
            from shorts_bot.integrations.meta_token_scrape import setup_meta_page_api

            msg = setup_meta_page_api(page_name=args.page_name)
        else:
            from shorts_bot.integrations.meta_app_create import setup_meta_app_and_token

            msg = setup_meta_app_and_token(
                app_name=args.app_name,
                page_name=args.page_name,
                wait_password_sec=args.password_wait,
            )
        console.print(f"[green]{msg}[/green]")
    except Exception as exc:
        console.print(f"[red]{exc}[/red]")
        console.print(
            "\nIf stuck on password: finish on Desktop, then run:\n"
            "  python3 -m shorts_bot.integrations.meta_app_create_cli --token-only"
        )
        raise SystemExit(1) from exc

    from shorts_bot.integrations.api_setup_cli import print_api_matrix

    console.print("")
    print_api_matrix()


if __name__ == "__main__":
    main()
