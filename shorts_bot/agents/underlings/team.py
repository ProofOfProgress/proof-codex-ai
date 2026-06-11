"""UnderlingTeam — manager-only facade. Humans talk to Chief Manager, not underlings."""

from __future__ import annotations

from typing import Callable

from shorts_bot.agents.priority import WorkPriority, user_wants_drafts
from shorts_bot.agents.runner import SpecialistRunner
from shorts_bot.agents.tasks import WorkLogEntry, WorkTaskRunner, default_topic_batch
from shorts_bot.agents.underlings.base import UnderlingResult
from shorts_bot.agents.underlings.research_lead import ResearchLead
from shorts_bot.config import settings

ProgressCallback = Callable[[str], None]


def _results_to_log(results: list[UnderlingResult]) -> list[WorkLogEntry]:
    return [r.to_work_log_entry() for r in results]


class UnderlingTeam:
    """Chief Manager dispatches work here — underlings never expose a user-facing chat."""

    def __init__(
        self,
        *,
        runner: SpecialistRunner | None = None,
        on_progress: ProgressCallback | None = None,
        priority: WorkPriority | None = None,
    ) -> None:
        self.runner = runner or SpecialistRunner()
        self.on_progress = on_progress or (lambda _m: None)
        self.priority = priority or WorkPriority(settings.manager_work_priority)
        self.research_lead = ResearchLead(self.runner, on_progress=on_progress)
        self.tasks = WorkTaskRunner(runner=self.runner, on_progress=on_progress)

    def plan_session(self, user_request: str, budget_seconds: int) -> WorkLogEntry:
        if self.priority == WorkPriority.RESEARCH:
            topics = default_topic_batch(5, user_request=user_request)
            plan = self.research_lead.plan_research_queue(user_request, budget_seconds, topics)
            role = "research_lead"
            summary = "Research queue planned"
        else:
            plan = self.tasks.plan_work(user_request, budget_seconds)
            role = "content_manager"
            summary = "Work plan for session"
        return WorkLogEntry(
            task="plan",
            role=role,
            summary=summary,
            elapsed_seconds=0,
            detail=plan,
        )

    def score_topics_batch(
        self,
        user_request: str,
        *,
        offset: int = 0,
        count: int = 5,
    ) -> WorkLogEntry:
        topics = default_topic_batch(count, offset=offset, user_request=user_request)
        return self.tasks.score_topics(topics, user_request)

    def research_topic_full(self, topic: str, *, user_request: str = "") -> list[WorkLogEntry]:
        results = self.research_lead.run_full_research(topic, user_request=user_request)
        return _results_to_log(results)

    def research_topic_deep(self, topic: str, *, user_request: str = "") -> WorkLogEntry:
        return self.research_lead.run_deep_only(topic, user_request=user_request).to_work_log_entry()

    def maybe_write_draft(
        self,
        topic: str,
        *,
        user_request: str,
        research_detail: str,
    ) -> WorkLogEntry | None:
        if self.priority == WorkPriority.RESEARCH and not user_wants_drafts(user_request):
            return None
        if self.priority == WorkPriority.BALANCED and not user_wants_drafts(user_request):
            return None
        return self.tasks.write_draft(topic, research_detail=research_detail)

    def maybe_review(self, label: str, text: str) -> WorkLogEntry | None:
        if self.priority == WorkPriority.RESEARCH:
            return None
        return self.tasks.review_text(label, text)
