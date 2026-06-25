"""CLI — talk to InVideo Agent One."""

from __future__ import annotations

import argparse

from rich.console import Console
from rich.panel import Panel

from shorts_bot.invideo.agent_one import probe_agent_one_session, send_prompt
from shorts_bot.invideo.prompts import DEFAULT_CHATGPT_PLUS_BRIEF

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(description="Send a prompt to InVideo Agent One chat")
    parser.add_argument("message", nargs="?", default=None, help="Prompt for Agent One")
    parser.add_argument("--open-browser", action="store_true", help="Visible browser — watch Agent One work")
    parser.add_argument("--wait", type=int, default=45, help="Seconds to wait for reply")
    parser.add_argument("--test", action="store_true", help="Check login + Agent mode only")
    args = parser.parse_args()

    if args.test:
        ok, detail = probe_agent_one_session()
        console.print(f"[green]{detail}[/green]" if ok else f"[red]{detail}[/red]")
        raise SystemExit(0 if ok else 1)

    message = args.message or DEFAULT_CHATGPT_PLUS_BRIEF
    console.print(
        Panel(
            "Agent One = InVideo's chat filmmaker (NOT our script generator).\n"
            "We send a brief → Agent One writes script + builds scenes → you approve Generate.",
            title="InVideo Agent One",
        )
    )

    try:
        result = send_prompt(
            message,
            open_browser=args.open_browser,
            wait_sec=args.wait,
        )
    except Exception as exc:
        console.print(f"[red]{exc}[/red]")
        console.print("[yellow]Login:[/yellow] python3 -m shorts_bot.invideo.handoff_cli")
        raise SystemExit(1) from exc

    console.print(f"[green]{result.message}[/green]")
    if result.project_url:
        console.print(f"\nProject:\n{result.project_url}")
    if result.response_excerpt:
        console.print(f"\n[dim]Agent excerpt:[/dim]\n{result.response_excerpt[:600]}")


if __name__ == "__main__":
    main()
