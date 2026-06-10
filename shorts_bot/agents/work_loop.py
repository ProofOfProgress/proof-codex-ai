"""Timed work loop — fill a duration budget with specialist tasks."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable

from shorts_bot.agents.duration import format_duration
from shorts_bot.agents.tasks import WorkLogEntry, WorkTaskRunner, default_topic_batch

ProgressCallback = Callable[[str], None]


@dataclass
class WorkSession:
    """Accumulates work until the time budget is exhausted."""

    budget_seconds: int
    user_request: str
    log: list[WorkLogEntry] = field(default_factory=list)
    started_at: float = field(default_factory=time.monotonic)

    @property
    def elapsed(self) -> float:
        return time.monotonic() - self.started_at

    @property
    def remaining(self) -> float:
        return max(0.0, self.budget_seconds - self.elapsed)

    @property
    def budget_exhausted(self) -> bool:
        return self.remaining <= 0

    def work_log_dicts(self) -> list[dict[str, Any]]:
        return [e.to_dict() for e in self.log]

    def context_for_synthesis(self) -> str:
        parts = [
            f"Work session: {format_duration(self.budget_seconds)} budget, "
            f"used {format_duration(int(self.elapsed))}.",
            f"User request: {self.user_request}",
            f"Tasks completed: {len(self.log)}",
        ]
        for entry in self.log:
            parts.append(f"\n## {entry.task} ({entry.role}) — {entry.summary}")
            if entry.artifacts:
                parts.append(f"Artifacts: {entry.artifacts}")
            parts.append(entry.detail[:2000])
        return "\n".join(parts)


def run_timed_work(
    user_request: str,
    budget_seconds: int,
    *,
    on_progress: ProgressCallback | None = None,
) -> WorkSession:
    """Run as much high-value work as fits in budget_seconds."""
    session = WorkSession(budget_seconds=budget_seconds, user_request=user_request)
    tasks = WorkTaskRunner(on_progress=on_progress)
    progress = on_progress or (lambda _m: None)

    # Always plan first if budget >= 2 min
    if budget_seconds >= 120:
        plan = tasks.plan_work(user_request, budget_seconds)
        session.log.append(
            WorkLogEntry(
                task="plan",
                role="content_manager",
                summary="Work plan for session",
                elapsed_seconds=0,
                detail=plan,
            )
        )

    topic_offset = 0
    top_topic: str | None = None
    last_research_detail = ""

    while not session.budget_exhausted:
        remaining = session.remaining

        # Phase 1: score topics (cheap, ~30-90s each batch)
        if remaining >= 45 and not any(e.task == "score_topics" for e in session.log[-2:]):
            batch_size = 3 if remaining < 300 else 5
            topics = default_topic_batch(batch_size, offset=topic_offset)
            topic_offset += batch_size
            entry = tasks.score_topics(topics, user_request)
            session.log.append(entry)
            # pick first topic as candidate for deeper work
            if topics and top_topic is None:
                top_topic = topics[0]
            progress(f"Done: {entry.summary} ({int(session.elapsed)}s elapsed)")
            continue

        # Phase 2: deep research on best topic
        if remaining >= 90 and top_topic and not any(
            e.task == "scout_research" and e.artifacts.get("topic") == top_topic for e in session.log
        ):
            entry = tasks.scout_research(top_topic)
            session.log.append(entry)
            last_research_detail = entry.detail
            progress(f"Done: {entry.summary}")
            continue

        # Phase 3: draft (expensive)
        if remaining >= 120 and top_topic and not any(
            e.task == "write_draft" for e in session.log
        ):
            entry = tasks.write_draft(top_topic, research_detail=last_research_detail)
            session.log.append(entry)
            progress(f"Done: {entry.summary}")
            # queue review if we have time
            if entry.detail and remaining >= 60:
                rev = tasks.review_text("draft script", entry.detail)
                session.log.append(rev)
            # next cycle: pick next topic
            top_topic = default_topic_batch(1, offset=topic_offset)[0]
            topic_offset += 1
            continue

        # Phase 4: more research on rotation topics if time left
        if remaining >= 90:
            next_topic = default_topic_batch(1, offset=topic_offset)[0]
            topic_offset += 1
            if not any(
                e.task == "scout_research" and e.artifacts.get("topic") == next_topic
                for e in session.log
            ):
                entry = tasks.scout_research(next_topic)
                session.log.append(entry)
                progress(f"Done: {entry.summary}")
                continue

        # Phase 5: quality pass on accumulated scoring
        score_entries = [e for e in session.log if e.task == "score_topics"]
        if remaining >= 45 and score_entries and not any(e.task == "quality_review" for e in session.log):
            rev = tasks.review_text("topic scores", score_entries[-1].detail)
            session.log.append(rev)
            continue

        # Nothing left that fits — exit
        break

    return session
