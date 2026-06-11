"""CLI: talk to the Chief Manager with optional work-duration budgets."""

from __future__ import annotations

import argparse
import sys

from rich.console import Console
from rich.panel import Panel
from shorts_bot.agents.duration import format_duration, parse_work_duration
from shorts_bot.agents.manager import ChiefManager
from shorts_bot.config import settings
from shorts_bot.llm.provider import chat_provider_label, get_llm_backend

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Don't Blink Chief Manager — delegates Gemini specialists."
    )
    parser.add_argument(
        "message",
        nargs="?",
        help='Request, e.g. "take an hour to plan cosy shorts this week"',
    )
    parser.add_argument(
        "--work",
        metavar="DURATION",
        help="Force work budget: 30m, 1h, 90s (overrides message parsing)",
    )
    args = parser.parse_args()

    if not args.message and not sys.stdin.isatty():
        args.message = sys.stdin.read().strip()

    backend = get_llm_backend()
    provider = chat_provider_label()
    console.print(
        Panel(
            "[bold]Chief Manager[/bold] — Don't Blink\n"
            f"LLM: [cyan]{provider}[/cyan]"
            + (f" ({backend.model})" if backend else " [yellow](offline)[/yellow]")
            + "\n\n"
            "Duration examples:\n"
            "  • [dim]take an hour to plan this week's cosy shorts[/dim]\n"
            "  • [dim][30m] score topics for RPM[/dim]\n"
            "  • [dim]don't respond for 45 minutes — research attachment hooks[/dim]\n\n"
            "Interactive: run with no args. One-shot: pass message as argument.",
            title="Manager",
            border_style="green",
        )
    )

    def progress(msg: str) -> None:
        console.print(f"[dim]… {msg}[/dim]")

    mgr = ChiefManager(on_progress=progress)

    def run_once(text: str) -> None:
        if args.work:
            from shorts_bot.agents.duration import clamp_work_seconds
            from shorts_bot.agents.manager import run_manager_job

            parsed = parse_work_duration(text)
            # parse --work value
            w = parse_work_duration(f"take {args.work} to work")
            seconds = w.work_seconds or settings.manager_work_floor_seconds
            seconds = clamp_work_seconds(
                seconds,
                minimum=settings.manager_work_floor_seconds,
                maximum=settings.manager_max_work_seconds,
            )
            console.print(f"[yellow]Forced work budget: {format_duration(seconds)}[/yellow]")
            result = run_manager_job(text, seconds, on_progress=progress)
        else:
            result = mgr.handle(text)

        if result.session:
            console.print(
                f"[dim]Completed {len(result.session.log)} tasks in "
                f"{format_duration(int(result.session.elapsed))}[/dim]"
            )
        console.print(Panel(result.reply, title="Chief Manager", border_style="blue"))

    if args.message:
        run_once(args.message)
        return

    while True:
        try:
            user_input = console.input("[bold yellow]manager>[/bold yellow] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\nBye.")
            break
        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit", "/exit", "/quit"}:
            console.print("Bye.")
            break
        run_once(user_input)


if __name__ == "__main__":
    main()
