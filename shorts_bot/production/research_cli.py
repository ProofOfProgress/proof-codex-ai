"""CLI: deep research for a topic before production."""

from __future__ import annotations

import argparse
import json

from rich.console import Console
from rich.panel import Panel

from shorts_bot.production.research import deep_research_topic, research_path, save_research

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(description="Deep research for YouTube Short production.")
    parser.add_argument("topic", nargs="?", default=None, help="Topic (default: next rotated)")
    parser.add_argument("--refresh", action="store_true", help="Ignore cache")
    args = parser.parse_args()

    topic = args.topic
    if not topic:
        from shorts_bot.config import settings
        from shorts_bot.memory.store import MemoryStore
        from shorts_bot.production.topic_rotation import next_topic

        store = MemoryStore(settings.database_path)
        topic = next_topic(store)

    research = deep_research_topic(topic, force_refresh=args.refresh)
    path = save_research(research)
    console.print(Panel(research.draft_context(), title=f"Research: {topic}"))
    console.print(f"[green]Saved {path}[/green]")
    console.print(json.dumps(research.to_dict(), indent=2)[:1200] + "...")


if __name__ == "__main__":
    main()
