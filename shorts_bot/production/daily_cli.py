"""Daily autopilot — AI draft → auto-approve → finish → upload."""

from __future__ import annotations

import argparse

from rich.console import Console

from shorts_bot.config import settings
from shorts_bot.drafts.generator import DraftGenerator
from shorts_bot.memory.store import MemoryStore
from shorts_bot.production.pipeline import finish_draft_pipeline
from shorts_bot.production.research import deep_research_topic
from shorts_bot.production.topic_rotation import next_topic

console = Console()


def run_daily(*, topic: str | None = None, upload: bool | None = None) -> str:
    store = MemoryStore(settings.database_path)
    topic = topic or next_topic(store)

    research = deep_research_topic(topic)
    gen = DraftGenerator(store)
    draft = gen.create_and_store(topic, research=research)
    messages = [
        f"Research: {research.viewer_moment[:80]}…",
        f"Draft #{draft.id} created: {topic}",
    ]

    if settings.auto_approve_drafts:
        store.review_draft(draft.id, "approved", "Auto-approved (AI pipeline)")
        messages.append(f"Auto-approved draft #{draft.id}")

    result = finish_draft_pipeline(store, draft.id, upload_youtube=upload)
    messages.extend(result.messages)
    if result.upload_url:
        messages.append(f"PUBLISHED: {result.upload_url}")

    return "\n".join(messages)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one full daily Short (fully AI).")
    parser.add_argument("--topic", default=None, help="Override rotated topic")
    parser.add_argument("--no-upload", action="store_true")
    args = parser.parse_args()
    upload = False if args.no_upload else None
    console.print(f"[green]{run_daily(topic=args.topic, upload=upload)}[/green]")


if __name__ == "__main__":
    main()
