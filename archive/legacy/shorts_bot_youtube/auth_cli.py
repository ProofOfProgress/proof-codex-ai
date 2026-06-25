"""Connect YouTube — API OAuth (trusted browser). Never uses Playwright for Google login."""

from __future__ import annotations

import argparse

from rich.console import Console
from rich.panel import Panel

from shorts_bot.youtube.google_auth import (
    auth_status,
    credentials_status_message,
    oauth_authorization_url,
    oauth_complete_redirect,
    run_oauth_flow,
    upload_ready,
)

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="YouTube OAuth — API upload (no Playwright / Studio browser login)."
    )
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("status", help="Show OAuth key + token status")

    sub.add_parser("connect", help="Open Google OAuth in Desktop/system browser (default)")

    url_p = sub.add_parser("url", help="Print OAuth URL for phone or home PC")
    url_p.add_argument(
        "--complete",
        metavar="REDIRECT_URL",
        help="Paste full redirect URL after sign-in (http://127.0.0.1:8090/?code=...)",
    )

    args = parser.parse_args()
    cmd = args.cmd or "connect"

    if cmd == "status":
        st = auth_status()
        console.print(Panel(credentials_status_message(), title="Google OAuth keys"))
        console.print(f"Token saved: {st['token_saved']}")
        console.print(f"API upload ready: {st['upload_ready']}")
        return

    if cmd == "url":
        if getattr(args, "complete", None):
            result = oauth_complete_redirect(args.complete)
            if result["ok"]:
                console.print(f"[green]{result['message']}[/green]")
            else:
                console.print(f"[red]{result['message']}[/red]")
            return
        try:
            url = oauth_authorization_url()
        except RuntimeError as exc:
            console.print(f"[red]{exc}[/red]")
            return
        console.print(
            Panel(
                "1. Open this URL on your **phone** or **home PC** (Chrome/Safari — NOT the bot browser)\n"
                "2. Sign in → Allow YouTube access\n"
                "3. Browser will try localhost — copy the **full address bar URL** "
                "(starts with http://127.0.0.1:8090/?code=)\n"
                "4. Run:\n"
                "   python3 -m shorts_bot.youtube.auth_cli url --complete 'PASTE_URL_HERE'",
                title="YouTube OAuth (trusted device)",
            )
        )
        console.print(url)
        return

    # connect (default)
    console.print(
        Panel(
            "Uses **Google OAuth** in your Desktop/system browser — NOT Playwright.\n"
            "Grants Analytics + **API video upload** — no YouTube Studio browser needed.",
            title="Connect YouTube",
        )
    )
    st = auth_status()
    if not st["credentials_configured"]:
        console.print(f"[red]{credentials_status_message()}[/red]")
        console.print(
            "\n[yellow]Alternative:[/yellow] run auth on home PC, add secret "
            "[bold]YOUTUBE_TOKEN_JSON[/bold] (full contents of data/youtube_token.json), "
            "then bash scripts/install.sh"
        )
        return
    if st.get("needs_upload_reauth"):
        console.print("[yellow]Token lacks upload scope — re-authorizing.[/yellow]")
    elif st.get("upload_ready"):
        console.print("[green]Already authorized — refreshing if needed.[/green]")

    console.print("[cyan]Click Desktop tab if a browser window opens…[/cyan]")
    result = run_oauth_flow(open_browser=True)
    if result["ok"]:
        console.print(f"[green]{result['message']}[/green]")
        if upload_ready():
            console.print("[green]API upload ready — pipeline uploads without Studio.[/green]")
    else:
        console.print(f"[red]{result['message']}[/red]")


if __name__ == "__main__":
    main()
