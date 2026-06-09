"""Connect YouTube Analytics — run once at home."""

from rich.console import Console
from rich.panel import Panel

from shorts_bot.youtube.google_auth import auth_status, run_oauth_flow

console = Console()


def main() -> None:
    console.print(Panel("YouTube Analytics OAuth\nA browser opens — sign in with your channel Google account.", title="Connect"))
    status = auth_status()
    if not status["credentials_configured"]:
        console.print("[red]Missing GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET in .env[/red]")
        console.print("See docs/TOMORROW.md for setup steps.")
        return
    result = run_oauth_flow()
    if result["ok"]:
        console.print(f"[green]{result['message']}[/green]")
    else:
        console.print(f"[red]{result['message']}[/red]")


if __name__ == "__main__":
    main()
