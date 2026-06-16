"""Daily autopilot — AI draft → auto-approve → finish → upload."""

from __future__ import annotations

import argparse

from rich.console import Console

from shorts_bot.brand.loader import ChannelBrand
from shorts_bot.config import settings
from shorts_bot.course.loader import CourseKnowledgeBase
from shorts_bot.course.router import CourseRouter
from shorts_bot.drafts.generator import DraftGenerator
from shorts_bot.memory.agent_memory import get_agent_memory_store
from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.memory.store import MemoryStore
from shorts_bot.llm.provider import get_llm_backend
from shorts_bot.production.pipeline import finish_draft_pipeline
from shorts_bot.production.research import deep_research_topic
from shorts_bot.production.topic_rotation import next_topic

console = Console()


def run_daily(*, topic: str | None = None, upload: bool | None = None) -> str:
    store = MemoryStore(settings.database_path)
    topic = topic or next_topic(store)

    research = deep_research_topic(topic, force_refresh=settings.daily_research_force_refresh)
    backend = get_llm_backend()
    memory = MemoryExtensions(store)
    kb = CourseKnowledgeBase(settings.course_dir)
    router = CourseRouter(kb)
    gen = DraftGenerator(
        store,
        client=backend.client if backend else None,
        model=backend.model if backend else settings.openai_model,
        router=router,
        memory=memory,
        agent_memory=get_agent_memory_store(store),
        brand=ChannelBrand(),
    )
    draft = gen.create_and_store(topic, research=research)
    messages = [
        f"Research: {research.viewer_moment[:80]}…",
        f"Draft #{draft.id} created: {topic}",
    ]

    if settings.auto_approve_drafts:
        from shorts_bot.learning.feedback import learn_from_draft

        store.review_draft(draft.id, "approved", "Auto-approved (AI pipeline)")
        learned = learn_from_draft(memory, draft.topic, "Auto-approved (AI pipeline)", "approved")
        messages.append(f"Auto-approved draft #{draft.id}")
        messages.append(learned)

    result = finish_draft_pipeline(store, draft.id, upload_youtube=upload)
    messages.extend(result.messages)
    if result.upload_url:
        messages.append(f"PUBLISHED: {result.upload_url}")

    return "\n".join(messages)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one full daily Short (fully AI).")
    parser.add_argument("--topic", default=None, help="Override rotated topic")
    parser.add_argument("--upload", action="store_true", help="Upload to YouTube after render")
    parser.add_argument("--no-upload", action="store_true")
    args = parser.parse_args()
    if args.upload and args.no_upload:
        parser.error("--upload and --no-upload cannot be used together")
    upload = False if args.no_upload else None
    if args.upload:
        upload = True
    console.print(f"[green]{run_daily(topic=args.topic, upload=upload)}[/green]")


if __name__ == "__main__":
    main()
