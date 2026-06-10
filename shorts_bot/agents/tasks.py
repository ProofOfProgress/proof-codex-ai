"""Concrete work units the manager delegates during a timed session."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable

from shorts_bot.agents.roles import (
    CONTENT_MANAGER,
    NICHE_STRATEGIST,
    QUALITY_REVIEWER,
    RESEARCH_SCOUT,
    SCRIPT_WRITER,
)
from shorts_bot.agents.runner import SpecialistRunner
from shorts_bot.config import settings
from shorts_bot.production.niche import DEFAULT_TOPICS, NICHE_POSITIONING


@dataclass
class WorkLogEntry:
    task: str
    role: str
    summary: str
    elapsed_seconds: float
    detail: str = ""
    artifacts: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "task": self.task,
            "role": self.role,
            "summary": self.summary,
            "elapsed_seconds": round(self.elapsed_seconds, 1),
            "detail": self.detail[:4000] if self.detail else "",
            "artifacts": self.artifacts,
        }


ProgressCallback = Callable[[str], None]


class WorkTaskRunner:
    """Runs pipeline tasks + Gemini specialists; respects time budget."""

    def __init__(
        self,
        *,
        runner: SpecialistRunner | None = None,
        on_progress: ProgressCallback | None = None,
    ) -> None:
        self.runner = runner or SpecialistRunner()
        self.on_progress = on_progress or (lambda _msg: None)

    def _log(self, msg: str) -> None:
        self.on_progress(msg)

    def plan_work(self, user_request: str, work_seconds: int) -> str:
        self._log("Content manager planning work queue…")
        return self.runner.run(
            CONTENT_MANAGER,
            f"User request: {user_request}\nTime budget: {work_seconds} seconds (~{work_seconds // 60} min).",
            context=NICHE_POSITIONING[:1500],
        )

    def score_topics(self, topics: list[str], user_request: str) -> WorkLogEntry:
        t0 = time.monotonic()
        self._log(f"Niche strategist scoring {len(topics)} topics…")
        task = "Score these topics:\n" + "\n".join(f"- {t}" for t in topics)
        if user_request:
            task += f"\n\nUser priority: {user_request}"
        result = self.runner.run(NICHE_STRATEGIST, task, context=NICHE_POSITIONING[:1200])
        return WorkLogEntry(
            task="score_topics",
            role=NICHE_STRATEGIST.name,
            summary=f"Scored {len(topics)} cosy/RPM topics",
            elapsed_seconds=time.monotonic() - t0,
            detail=result,
            artifacts={"topics": topics},
        )

    def scout_research(self, topic: str) -> WorkLogEntry:
        t0 = time.monotonic()
        self._log(f"Research scout: {topic[:60]}…")

        detail = self.runner.run(RESEARCH_SCOUT, f"Topic: {topic}")

        # Also run cached deep research when available (heavier, real data)
        artifacts: dict[str, Any] = {"topic": topic}
        try:
            from shorts_bot.production.research import deep_research_topic

            pr = deep_research_topic(topic, force_refresh=False)
            artifacts["research_slug"] = pr.topic
            artifacts["hooks"] = pr.hook_angles[:4]
            detail += "\n\n--- DEEP RESEARCH (cached pipeline) ---\n"
            detail += pr.draft_context()[:2500]
        except Exception as exc:
            detail += f"\n\n(deep research skipped: {exc})"

        return WorkLogEntry(
            task="scout_research",
            role=RESEARCH_SCOUT.name,
            summary=f"Research on: {topic[:80]}",
            elapsed_seconds=time.monotonic() - t0,
            detail=detail,
            artifacts=artifacts,
        )

    def write_draft(self, topic: str, *, research_detail: str = "") -> WorkLogEntry:
        t0 = time.monotonic()
        self._log(f"Script worker drafting: {topic[:60]}…")
        context = research_detail[:3000] if research_detail else ""
        script_out = self.runner.run(
            SCRIPT_WRITER,
            f"Topic: {topic}",
            context=context,
        )

        draft_id: int | None = None
        try:
            from shorts_bot.approval.queue import ApprovalQueue
            from shorts_bot.brand.loader import ChannelBrand
            from shorts_bot.course.loader import CourseKnowledgeBase
            from shorts_bot.course.router import CourseRouter
            from shorts_bot.drafts.generator import DraftGenerator
            from shorts_bot.llm.provider import get_llm_backend
            from shorts_bot.memory.agent_memory import get_agent_memory_store
            from shorts_bot.memory.extensions import MemoryExtensions
            from shorts_bot.memory.store import MemoryStore

            backend = get_llm_backend()
            store = MemoryStore(settings.database_path)
            kb = CourseKnowledgeBase(settings.course_dir)
            router = CourseRouter(kb)
            gen = DraftGenerator(
                store,
                client=backend.client if backend else None,
                model=backend.model if backend else settings.openai_model,
                router=router,
                memory=MemoryExtensions(store),
                agent_memory=get_agent_memory_store(store),
                brand=ChannelBrand(),
            )
            draft = gen.create_and_store(topic)
            draft_id = draft.id
            script_out += f"\n\n--- PIPELINE DRAFT #{draft_id} ---\nHook: {draft.hook}\n"
        except Exception as exc:
            script_out += f"\n\n(pipeline draft skipped: {exc})"

        return WorkLogEntry(
            task="write_draft",
            role=SCRIPT_WRITER.name,
            summary=f"Draft for: {topic[:80]}" + (f" → #{draft_id}" if draft_id else ""),
            elapsed_seconds=time.monotonic() - t0,
            detail=script_out,
            artifacts={"topic": topic, "draft_id": draft_id},
        )

    def review_text(self, label: str, text: str) -> WorkLogEntry:
        t0 = time.monotonic()
        self._log(f"Quality review: {label[:40]}…")
        result = self.runner.run(QUALITY_REVIEWER, f"Review this {label}:\n\n{text[:3500]}")
        return WorkLogEntry(
            task="quality_review",
            role=QUALITY_REVIEWER.name,
            summary=f"Reviewed {label[:60]}",
            elapsed_seconds=time.monotonic() - t0,
            detail=result,
        )


def default_topic_batch(count: int, *, offset: int = 0) -> list[str]:
    n = len(DEFAULT_TOPICS)
    if n == 0:
        return ["the minute before you can't move from the couch"]
    return [DEFAULT_TOPICS[(offset + i) % n] for i in range(count)]
