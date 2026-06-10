"""Timed work loop — research-priority scheduling via UnderlingTeam."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable

from shorts_bot.agents.duration import format_duration
from shorts_bot.agents.priority import WorkPriority, user_wants_drafts
from shorts_bot.agents.tasks import WorkLogEntry, default_topic_batch
from shorts_bot.agents.underlings.team import UnderlingTeam
from shorts_bot.config import settings

ProgressCallback = Callable[[str], None]


@dataclass
class WorkSession:
    """Accumulates work until the time budget is exhausted."""

    budget_seconds: int
    user_request: str
    log: list[WorkLogEntry] = field(default_factory=list)
    started_at: float = field(default_factory=time.monotonic)
    priority: WorkPriority = field(default_factory=lambda: WorkPriority(settings.manager_work_priority))

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

    def researched_topics(self) -> list[str]:
        topics: list[str] = []
        for e in self.log:
            t = e.artifacts.get("topic")
            if t and e.task in {"deep_research", "scout_brief", "competitor_analysis", "hook_analysis"}:
                if t not in topics:
                    topics.append(t)
        return topics

    def research_files(self) -> list[str]:
        files: list[str] = []
        for e in self.log:
            f = e.artifacts.get("research_file")
            if f and f not in files:
                files.append(f)
        return files

    def context_for_synthesis(self) -> str:
        parts = [
            f"Work session: {format_duration(self.budget_seconds)} budget, "
            f"used {format_duration(int(self.elapsed))}.",
            f"Priority: {self.priority.value}",
            f"User request: {self.user_request}",
            f"Tasks completed: {len(self.log)}",
        ]
        rfiles = self.research_files()
        if rfiles:
            parts.append("Research files: " + ", ".join(rfiles))
        for entry in self.log:
            parts.append(f"\n## {entry.task} ({entry.role}) — {entry.summary}")
            if entry.artifacts:
                parts.append(f"Artifacts: {entry.artifacts}")
            parts.append(entry.detail[:2000])
        return "\n".join(parts)


def _pick_next_topic(session: WorkSession, offset: int) -> str:
    researched = set(session.researched_topics())
    for i in range(len(default_topic_batch(1))):
        candidate = default_topic_batch(1, offset=offset + i)[0]
        if candidate not in researched:
            return candidate
    return default_topic_batch(1, offset=offset)[0]


def run_timed_work(
    user_request: str,
    budget_seconds: int,
    *,
    on_progress: ProgressCallback | None = None,
    priority: WorkPriority | None = None,
) -> WorkSession:
    """Fill time budget — research priority by default."""
    prio = priority or WorkPriority(settings.manager_work_priority)
    session = WorkSession(
        budget_seconds=budget_seconds,
        user_request=user_request,
        priority=prio,
    )
    team = UnderlingTeam(on_progress=on_progress, priority=prio)
    progress = on_progress or (lambda _m: None)

    if budget_seconds >= 60:
        session.log.append(team.plan_session(user_request, budget_seconds))

    topic_offset = 0
    full_stack_done = 0
    deep_only_done = 0
    score_passes = 0
    max_full_stacks = 3 if budget_seconds >= 600 else (2 if budget_seconds >= 300 else 1)
    max_deep_only = max(2, budget_seconds // 45)
    max_iterations = max(24, budget_seconds // 5)
    iterations = 0

    while not session.budget_exhausted and iterations < max_iterations:
        iterations += 1
        remaining = session.remaining

        # --- RESEARCH PRIORITY LOOP ---
        if prio == WorkPriority.RESEARCH:
            # Light topic score once early (feeds research targets)
            if (
                remaining >= 40
                and score_passes < 1
                and not user_wants_drafts(user_request)
            ):
                count = 5 if remaining >= 180 else 3
                entry = team.score_topics_batch(user_request, offset=topic_offset, count=count)
                topic_offset += count
                score_passes += 1
                session.log.append(entry)
                progress(f"Done: {entry.summary}")
                continue

            # Full research stack on next topic (main work unit ~2-4 min each)
            if remaining >= 75 and full_stack_done < max_full_stacks:
                topic = _pick_next_topic(session, topic_offset)
                topic_offset += 1
                if not any(
                    e.task == "deep_research" and e.artifacts.get("topic") == topic
                    for e in session.log
                ):
                    entries = team.research_topic_full(topic, user_request=user_request)
                    session.log.extend(entries)
                    full_stack_done += 1
                    progress(f"Done: full research stack on {topic[:50]}")
                    continue

            # Deep-only passes on more topics if time remains
            if remaining >= 50 and deep_only_done < max_deep_only:
                topic = _pick_next_topic(session, topic_offset)
                topic_offset += 1
                if not any(
                    e.task == "deep_research" and e.artifacts.get("topic") == topic
                    for e in session.log
                ):
                    entry = team.research_topic_deep(topic)
                    session.log.append(entry)
                    deep_only_done += 1
                    progress(f"Done: {entry.summary}")
                    continue

            # Drafts only if human explicitly asked
            if remaining >= 120 and user_wants_drafts(user_request):
                topic = _pick_next_topic(session, 0)
                last_detail = ""
                for e in reversed(session.log):
                    if e.task == "deep_research":
                        last_detail = e.detail
                        break
                draft_entry = team.maybe_write_draft(
                    topic, user_request=user_request, research_detail=last_detail
                )
                if draft_entry:
                    session.log.append(draft_entry)
                    progress(f"Done: {draft_entry.summary}")
                    continue

            break

        # --- BALANCED / PRODUCTION (legacy ordering) ---
        if remaining >= 45 and score_passes < 2:
            batch_size = 3 if remaining < 300 else 5
            entry = team.score_topics_batch(user_request, offset=topic_offset, count=batch_size)
            topic_offset += batch_size
            score_passes += 1
            session.log.append(entry)
            progress(f"Done: {entry.summary}")
            continue

        if remaining >= 90:
            topic = _pick_next_topic(session, topic_offset)
            topic_offset += 1
            entries = team.research_topic_full(topic, user_request=user_request)
            session.log.extend(entries)
            progress(f"Done: research on {topic[:50]}")
            continue

        if remaining >= 120 and (prio == WorkPriority.PRODUCTION or user_wants_drafts(user_request)):
            topic = _pick_next_topic(session, 0)
            last_detail = next(
                (e.detail for e in reversed(session.log) if e.task == "deep_research"),
                "",
            )
            draft_entry = team.maybe_write_draft(
                topic, user_request=user_request, research_detail=last_detail
            )
            if draft_entry:
                session.log.append(draft_entry)
                if remaining >= 60:
                    rev = team.maybe_review("draft script", draft_entry.detail)
                    if rev:
                        session.log.append(rev)
            break

        break

    return session
