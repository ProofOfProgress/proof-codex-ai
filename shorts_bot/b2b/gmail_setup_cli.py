"""CLI — create dedicated B2B outreach Gmail in browser."""

from __future__ import annotations

import argparse

from rich.console import Console
from rich.panel import Panel

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(description="Create B2B outreach Gmail (browser)")
    parser.add_argument("--headless", action="store_true", help="Headless (usually fails at CAPTCHA)")
    parser.add_argument("--minutes", type=int, default=25, help="How long to keep browser open")
    parser.add_argument("--first-name", default="Kim")
    parser.add_argument("--last-name", default="Rapid Tool Review")
    args = parser.parse_args()

    from shorts_bot.b2b.gmail_setup import B2BGmailSetup

    console.print(
        Panel(
            "Creating a **new** Gmail for B2B outreach.\n"
            "Uses a separate browser profile — does **not** touch PayPal ops Gmail.\n\n"
            "**Your turn:** Google will ask for a phone code on the Desktop tab.",
            title="B2B outreach Gmail setup",
        )
    )

    result = B2BGmailSetup(headless=args.headless, wait_minutes=args.minutes).run(
        first_name=args.first_name,
        last_name=args.last_name,
    )

    style = {"created": "green", "needs_human": "yellow", "failed": "red"}.get(result.status, "white")
    console.print(Panel(result.message, title=f"Status: {result.status}", border_style=style))

    if result.email:
        console.print(f"Outreach email: [cyan]{result.email}[/cyan]")
    if result.password and result.status in {"created", "needs_human"}:
        console.print(
            "[yellow]Password generated — saved to data/b2b/gmail_setup_handoff.json "
            "(local only, not committed).[/yellow]"
        )
    if result.screenshot_path:
        console.print(f"Screenshot: {result.screenshot_path}")
    if result.handoff_path:
        console.print(f"Handoff file: {result.handoff_path}")

    if result.status == "needs_human":
        console.print(
            "\n[bold]Open Cursor → Desktop tab[/bold] → finish phone verification.\n"
            "Then: Google Account → Security → App passwords → add to Cursor Secrets as B2B_SMTP_*"
        )
        raise SystemExit(2)
    if result.status == "failed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
