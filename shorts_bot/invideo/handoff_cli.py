"""Browser handoff — log into InVideo + optional API key."""

from __future__ import annotations

import argparse
import time

from rich.console import Console
from rich.panel import Panel

console = Console()

LOGIN_URL = "https://ai.invideo.io/login"
APP_HOME = "https://ai.invideo.io/"
SETTINGS_HINT = "https://ai.invideo.io/"


def _open_single_session(urls: list[tuple[str, str]], *, minutes: int = 15) -> None:
    from shorts_bot.browser.session import _has_display, _launch_context

    if not _has_display():
        console.print("[yellow]No Desktop — open these URLs on your PC:[/yellow]")
        for _label, url in urls:
            console.print(f"  {url}")
        return

    console.print("[cyan]Opening Desktop browser — stay in this window.[/cyan]")
    pw, context = _launch_context(headless=False)
    try:
        page = context.pages[0] if context.pages else context.new_page()
        for label, url in urls:
            console.print(f"[bold]{label}[/bold]")
            console.print(f"[dim]{url}[/dim]")
            page.goto(url, wait_until="domcontentloaded", timeout=120000)
            time.sleep(3)
        console.print(
            f"[yellow]Complete login in Desktop tab. Window closes in ~{minutes} min.[/yellow]"
        )
        time.sleep(minutes * 60)
    finally:
        context.close()
        pw.stop()


def run_wizard(*, login_only: bool = False) -> int:
    from shorts_bot.invideo.auth import auth_status

    st = auth_status()
    console.print(
        Panel(
            "Step 1 — Log into InVideo AI\n"
            "• Use Google or email (Google works without your broken phone)\n"
            "• Create your AI twin if InVideo asks\n\n"
            "Step 2 — (Optional) API key\n"
            "• Settings → Developers → copy API key\n"
            "• Add INVIDEO_API_KEY to Cursor Secrets → bash scripts/install.sh\n\n"
            "Step 3 — Test\n"
            "• Agent runs: python3 -m shorts_bot.invideo.generate_cli --draft-id 1 --open-browser",
            title="InVideo setup",
        )
    )

    if st["browser_logged_in"]:
        console.print("[green]Browser already logged into InVideo.[/green]")
    else:
        _open_single_session(
            [
                ("Step 1 — Log in to InVideo AI", LOGIN_URL),
                ("Step 2 — InVideo home (confirm login)", APP_HOME),
            ],
            minutes=12,
        )

    if not login_only:
        from shorts_bot.invideo.mcp_client import probe_mcp

        mcp_ok, mcp_detail = probe_mcp()
        if mcp_ok:
            console.print(f"[green]MCP: {mcp_detail}[/green]")
        else:
            console.print(f"[yellow]MCP: {mcp_detail}[/yellow]")

    console.print("\n[bold]Verify:[/bold] python3 -m shorts_bot.invideo.auth_cli status")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="InVideo browser login wizard")
    parser.add_argument("--login-only", action="store_true")
    args = parser.parse_args()
    raise SystemExit(run_wizard(login_only=args.login_only))


if __name__ == "__main__":
    main()
