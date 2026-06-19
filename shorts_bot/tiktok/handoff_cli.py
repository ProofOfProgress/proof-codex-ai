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


def _open_single_session(urls: list[tuple[str, str]], *, minutes: int = 20) -> None:
    """One Chromium window — avoids profile lock from multiple spawn_visible_browser calls."""
    from shorts_bot.browser.session import _has_display, _launch_context

    if not _has_display():
        console.print("[yellow]No Desktop display — open these URLs on your phone/PC:[/yellow]")
        for _label, url in urls:
            console.print(f"  {url}")
        return

    console.print("[cyan]Opening one Desktop browser window (stay in this tab).[/cyan]")
    pw, context = _launch_context(headless=False)
    try:
        page = context.pages[0] if context.pages else context.new_page()
        for label, url in urls:
            console.print(f"[bold]{label}[/bold]")
            console.print(f"[dim]{url}[/dim]")
            page.goto(url, wait_until="domcontentloaded", timeout=120000)
            time.sleep(3)
        console.print(
            "[yellow]Browser open — complete login + Allow in Desktop tab. "
            f"Auto-closes in ~{minutes} min.[/yellow]"
        )
        time.sleep(minutes * 60)
    finally:
        context.close()
        pw.stop()


def run_wizard(*, oauth_only: bool = False) -> int:
    from shorts_bot.tiktok.oauth import (
        auth_status,
        credentials_status_message,
        oauth_authorization_url_with_pkce,
        run_oauth_flow,
    )

    st = auth_status()
    console.print(Panel(credentials_status_message(), title="TikTok app keys"))
    if not st["credentials_configured"]:
        console.print("[red]Add TIKTOK_CLIENT_KEY + TIKTOK_CLIENT_SECRET first.[/red]")
        return 1

    auth_url = ""
    if not st["upload_ready"]:
        auth_url, _ = oauth_authorization_url_with_pkce()

    if not oauth_only:
        console.print(
            Panel(
                "Step 1 — Developer portal (verify redirect URI)\n"
                "• Content Posting API + Direct Post enabled\n"
                "• Redirect URI exactly: http://127.0.0.1:8091/\n\n"
                "Step 2 — OAuth — log into YOUR new TikTok → Allow\n\n"
                "Step 3 — Profile polish (optional) — name + bio",
                title="TikTok setup wizard",
            )
        )

    if st["upload_ready"]:
        console.print("[green]TikTok upload already connected.[/green]")
    else:
        console.print("[bold]Starting OAuth listener on :8091 — log in and tap Allow.[/bold]")
        if not oauth_only and auth_url:
            import threading

            browser_thread = threading.Thread(
                target=_open_single_session,
                kwargs={
                    "urls": [
                        ("Step 1 — TikTok Developer Portal", DEV_PORTAL),
                        ("Step 2 — TikTok OAuth (log in → Allow)", auth_url),
                    ],
                    "minutes": 12,
                },
                daemon=True,
            )
            browser_thread.start()
            time.sleep(5)
        result = run_oauth_flow(open_browser=oauth_only, timeout_sec=300, auth_url=auth_url or None)
        if result.get("ok"):
            console.print(f"[green]{result['message']}[/green]")
            console.print(f"Scopes: {result.get('scope', '')}")
        else:
            console.print(f"[red]{result.get('message')}[/red]")
            if result.get("auth_url"):
                console.print(f"\nManual URL:\n{result['auth_url']}")
            return 1

    if not oauth_only:
        _open_single_session(
            [
                ("TikTok home", TIKTOK_HOME),
                ("Edit profile", PROFILE_EDIT),
            ],
            minutes=8,
        )
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
