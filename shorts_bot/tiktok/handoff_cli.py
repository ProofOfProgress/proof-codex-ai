"""Browser handoff — TikTok account + developer OAuth."""

from __future__ import annotations

import argparse
import time

from rich.console import Console
from rich.panel import Panel

console = Console()

DEV_PORTAL = "https://developers.tiktok.com/apps/"
TIKTOK_HOME = "https://www.tiktok.com/"
PROFILE_EDIT = "https://www.tiktok.com/setting/profile"


def _open_visible(url: str, *, minutes: int = 10, label: str) -> None:
    from shorts_bot.browser.session import spawn_visible_browser

    console.print(f"[cyan]Opening Desktop browser:[/cyan] {label}")
    console.print(f"[dim]{url}[/dim]")
    console.print("[yellow]Click the Desktop tab in Cursor → sign in / complete steps there.[/yellow]")
    spawn_visible_browser(url, minutes=minutes)


def run_wizard(*, oauth_only: bool = False) -> int:
    from shorts_bot.tiktok.oauth import auth_status, credentials_status_message, run_oauth_flow

    st = auth_status()
    console.print(Panel(credentials_status_message(), title="TikTok app keys"))
    if not st["credentials_configured"]:
        console.print("[red]Add TIKTOK_CLIENT_KEY + TIKTOK_CLIENT_SECRET first.[/red]")
        return 1

    if not oauth_only:
        console.print(
            Panel(
                "Step 1 — Developer portal (verify redirect URI)\n"
                "• Content Posting API + Direct Post enabled\n"
                "• Redirect URI exactly: http://127.0.0.1:8091/\n\n"
                "Step 2 — OAuth (auto-opens) — log into YOUR new TikTok → Allow\n\n"
                "Step 3 — Profile polish (optional) — name + bio",
                title="TikTok setup wizard",
            )
        )
        _open_visible(DEV_PORTAL, minutes=8, label="TikTok Developer Portal")
        console.print("[dim]Waiting 15s for portal tab to load…[/dim]")
        time.sleep(15)

    if st["upload_ready"]:
        console.print("[green]TikTok upload already connected.[/green]")
    else:
        console.print("[bold]Starting OAuth — watch Desktop browser, log in, tap Allow.[/bold]")
        result = run_oauth_flow(open_browser=True, timeout_sec=300)
        if result.get("ok"):
            console.print(f"[green]{result['message']}[/green]")
            console.print(f"Scopes: {result.get('scope', '')}")
        else:
            console.print(f"[red]{result.get('message')}[/red]")
            if result.get("auth_url"):
                console.print(f"\nManual URL:\n{result['auth_url']}")
            return 1

    if not oauth_only:
        _open_visible(TIKTOK_HOME, minutes=5, label="TikTok home — confirm logged in")
        time.sleep(5)
        _open_visible(PROFILE_EDIT, minutes=10, label="Edit profile")
        console.print(
            Panel(
                "Suggested bio (paste in profile):\n\n"
                "Honest AI product reviews — Pay, Skip, or Wait in 30 seconds.\n"
                "No hype. Real tools tested so you don't waste money.\n\n"
                "Name ideas: AI Verdict / Skip Or Pay / Actually Tested AI",
                title="Profile copy",
            )
        )

    console.print("\n[bold]Verify:[/bold] python3 -m shorts_bot.tiktok.auth_cli status")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="TikTok browser setup wizard")
    parser.add_argument("--oauth-only", action="store_true", help="Skip portal/profile — OAuth only")
    args = parser.parse_args()
    raise SystemExit(run_wizard(oauth_only=args.oauth_only))


if __name__ == "__main__":
    main()
