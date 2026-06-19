"""Connect TikTok — Content Posting API OAuth."""

from __future__ import annotations

import argparse
import webbrowser

from rich.console import Console
from rich.panel import Panel

from shorts_bot.tiktok.oauth import (
    auth_status,
    credentials_status_message,
    oauth_authorization_url,
    oauth_complete_redirect,
    requested_scopes,
    redirect_uri,
)

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(description="TikTok OAuth for Content Posting API")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("status", help="Show TikTok app + token status")

    sub.add_parser("connect", help="Open TikTok OAuth in browser")

    url_p = sub.add_parser("url", help="Print OAuth URL or complete redirect")
    url_p.add_argument(
        "--complete",
        metavar="REDIRECT_URL",
        help="Paste redirect URL after login (http://127.0.0.1:8091/?code=...)",
    )

    args = parser.parse_args()
    cmd = args.cmd or "connect"

    if cmd == "status":
        st = auth_status()
        console.print(Panel(credentials_status_message(), title="TikTok developer app"))
        console.print(f"Token saved: {st['token_saved']}")
        console.print(f"Upload ready: {st['upload_ready']}")
        console.print(f"Scopes: {', '.join(st['scopes']) or '(none)'}")
        console.print(f"Redirect URI: {st['redirect_uri']}")
        return

    if cmd == "url":
        if getattr(args, "complete", None):
            result = oauth_complete_redirect(args.complete)
            if result.get("ok"):
                console.print(f"[green]{result['message']}[/green]")
                console.print(f"Scopes: {result.get('scope')}")
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
                "1. Open URL on your phone or PC browser\n"
                "2. Log into TikTok → Allow posting access\n"
                "3. Copy full redirect URL from address bar\n"
                "4. Run:\n"
                "   python3 -m shorts_bot.tiktok.auth_cli url --complete 'PASTE_URL'",
                title="TikTok OAuth",
            )
        )
        console.print(url)
        return

    console.print(
        Panel(
            f"Scopes: {', '.join(requested_scopes())}\n"
            f"Redirect: {redirect_uri()}\n\n"
            "Note: Unaudited TikTok apps may only post **private** until app audit passes.",
            title="TikTok connect",
        )
    )
    try:
        url = oauth_authorization_url()
    except RuntimeError as exc:
        console.print(f"[red]{exc}[/red]")
        return
    console.print(url)
    try:
        webbrowser.open(url)
    except Exception:
        pass
    console.print(
        "\nAfter Allow, paste redirect URL:\n"
        "  python3 -m shorts_bot.tiktok.auth_cli url --complete 'http://127.0.0.1:8091/?code=...'"
    )


if __name__ == "__main__":
    main()
