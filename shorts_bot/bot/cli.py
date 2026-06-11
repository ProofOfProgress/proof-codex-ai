from __future__ import annotations

import sys

from rich.console import Console
from rich.panel import Panel

from shorts_bot.approval.queue import ApprovalQueue
from shorts_bot.bot.agent import ShortsBotAgent
from shorts_bot.brand.loader import ChannelBrand
from shorts_bot.bot.tools import ToolRunner
from shorts_bot.config import settings
from shorts_bot.course.loader import CourseKnowledgeBase
from shorts_bot.course.router import CourseRouter
from shorts_bot.drafts.generator import DraftGenerator
from shorts_bot.agents.manager import ChiefManager, should_use_manager
from shorts_bot.llm.provider import get_llm_backend
from shorts_bot.memory.store import MemoryStore

console = Console()


def build_agent() -> ShortsBotAgent:
    store = MemoryStore(settings.database_path)
    kb = CourseKnowledgeBase(settings.course_dir)
    router = CourseRouter(kb)
    backend = get_llm_backend()
    brand = ChannelBrand()
    generator = DraftGenerator(
        store,
        client=backend.client if backend else None,
        model=backend.model if backend else None,
        router=router,
        brand=brand,
    )
    queue = ApprovalQueue(store)
    tools = ToolRunner(store, generator, queue, router=router)
    return ShortsBotAgent(
        store,
        tools,
        backend.client if backend else None,
        router,
        kb,
        brand,
        llm_model=backend.model if backend else None,
        llm_provider=backend.provider if backend else "offline",
    )


def main() -> None:
    agent = build_agent()
    backend = get_llm_backend()
    if backend:
        mode = f"Jenny strategist + {backend.provider}"
        model = backend.model
    else:
        mode = "offline + course routing"
        model = "none"
    console.print(
        Panel(
            "[bold]Don't Blink[/bold] — self-help Shorts strategist (Jenny course + brand voice)\n"
            f"Mode: [cyan]{mode}[/cyan] | Model: {model}\n"
            "Course files 01–09 loaded. Free-first stack: CapCut, YouTube Audio Library, Canva.\n"
            "Talk about ideas, drafts, hooks, retention — or approve/reject scripts.\n"
            "Chief Manager: [dim]take 30m to plan cosy shorts[/dim] or [dim]manager: score topics[/dim]\n"
            "Dedicated manager CLI: [dim]python3 -m shorts_bot.agents.cli[/dim]\n"
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

        if should_use_manager(user_input):

            def progress(msg: str) -> None:
                console.print(f"[dim]… {msg}[/dim]")

            result = ChiefManager(on_progress=progress).handle(user_input)
            console.print(Panel(result.reply, title="Chief Manager", border_style="blue"))
        else:
            reply = agent.chat(user_input)
            console.print(Panel(reply, title="bot", border_style="blue"))


if __name__ == "__main__":
    main()
