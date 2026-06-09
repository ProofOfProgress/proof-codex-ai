from __future__ import annotations

import sys

from openai import OpenAI
from rich.console import Console
from rich.panel import Panel

from shorts_bot.approval.queue import ApprovalQueue
from shorts_bot.bot.agent import ShortsBotAgent
from shorts_bot.bot.tools import ToolRunner
from shorts_bot.config import settings
from shorts_bot.drafts.generator import DraftGenerator
from shorts_bot.memory.store import MemoryStore

console = Console()


def build_agent() -> ShortsBotAgent:
    store = MemoryStore(settings.database_path)
    client = OpenAI(api_key=settings.openai_api_key) if settings.has_openai else None
    generator = DraftGenerator(store, client=client)
    queue = ApprovalQueue(store)
    tools = ToolRunner(store, generator, queue)
    return ShortsBotAgent(store, tools, client)


def main() -> None:
    agent = build_agent()
    mode = "OpenAI" if settings.has_openai else "offline"
    console.print(
        Panel(
            "[bold]Shorts Bot[/bold] — faceless YouTube Shorts operator\n"
            f"Mode: [cyan]{mode}[/cyan] | Model: {settings.openai_model}\n"
            "Talk to me about ideas, drafts, and approvals.\n"
            "Type [bold]exit[/bold] or [bold]quit[/bold] to leave.",
            title="Shorts Bot",
            border_style="green",
        )
    )

    while True:
        try:
            user_input = console.input("[bold yellow]you>[/bold yellow] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\nBye.")
            sys.exit(0)

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit", "/exit", "/quit"}:
            console.print("Bye.")
            break

        reply = agent.chat(user_input)
        console.print(Panel(reply, title="bot", border_style="blue"))


if __name__ == "__main__":
    main()
