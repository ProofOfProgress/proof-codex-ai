"""Connect YouTube — Analytics + API upload (one Google sign-in, no Playwright)."""

from rich.console import Console
from rich.panel import Panel

from shorts_bot.youtube.google_auth import auth_status, run_oauth_flow, upload_ready

console = Console()


def main() -> None:
    console.print(
        Panel(
            "YouTube OAuth\n"
            "Opens your system browser for Google sign-in (not Playwright).\n"
            "Grants Analytics + **API video upload** — no Studio browser automation.",
            title="Connect",
        )
    )
    status = auth_status()
    if not status["credentials_configured"]:
        console.print("[red]Missing GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET[/red]")
        console.print("Add them to Cursor secrets — install.sh syncs to .env automatically.")
        console.print("See docs/TOMORROW.md")
        return
    if status.get("needs_upload_reauth"):
        console.print(
            "[yellow]Existing token lacks upload scope — re-authorizing with upload enabled.[/yellow]"
        )
    elif status.get("upload_ready"):
        console.print("[green]YouTube API upload already authorized.[/green]")
        console.print("Re-running will refresh the token if needed.")
    result = run_oauth_flow()
    if result["ok"]:
        console.print(f"[green]{result['message']}[/green]")
        if upload_ready():
            console.print("[green]API upload ready — finish pipeline uploads without Studio browser.[/green]")
        else:
            console.print("[yellow]Upload scope still missing — try again with consent prompt.[/yellow]")
    else:
        console.print(f"[red]{result['message']}[/red]")


if __name__ == "__main__":
    main()
