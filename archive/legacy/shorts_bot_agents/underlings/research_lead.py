"""Research Lead — mini-manager for research underlings (manager-only)."""

from __future__ import annotations

import time
from typing import Callable

from shorts_bot.agents.roles import RESEARCH_LEAD
from shorts_bot.agents.runner import SpecialistRunner
from shorts_bot.agents.underlings.base import UnderlingResult, append_underling_log
from shorts_bot.agents.underlings.research_workers import (
    CompetitorAnalystUnderling,
    DeepResearchUnderling,
    HookAnalystUnderling,
    ResearchScoutUnderling,
    TrendsScoutUnderling,
)
from shorts_bot.agents.research_topics import ai_video_context_block, user_wants_ai_video_research
from shorts_bot.production.niche import NICHE_POSITIONING

ProgressCallback = Callable[[str], None]


class ResearchLead:
    """Coordinates research underlings. Only Chief Manager calls this."""

    name = "research_lead"

    def __init__(
        self,
        runner: SpecialistRunner,
        *,
        on_progress: ProgressCallback | None = None,
    ) -> None:
        self.runner = runner
        self.on_progress = on_progress or (lambda _m: None)
        self.scout = ResearchScoutUnderling(runner, on_progress=on_progress)
        self.deep = DeepResearchUnderling(runner, on_progress=on_progress)
        self.competitor = CompetitorAnalystUnderling(runner, on_progress=on_progress)
        self.hooks = HookAnalystUnderling(runner, on_progress=on_progress)
        self.trends = TrendsScoutUnderling(runner, on_progress=on_progress)

    def _progress(self, msg: str) -> None:
        self.on_progress(f"[{self.name}] {msg}")
        append_underling_log(f"{self.name}: {msg}")

    def plan_research_queue(self, user_request: str, budget_seconds: int, topics: list[str]) -> str:
        self._progress("planning research queue…")
        topic_list = "\n".join(f"- {t}" for t in topics[:8])
        ctx = (
            ai_video_context_block()
            if user_wants_ai_video_research(user_request)
            else NICHE_POSITIONING[:1200]
        )
        return self.runner.run(
            RESEARCH_LEAD,
            f"User request: {user_request}\n"
            f"Time budget: {budget_seconds}s\n"
            f"Candidate topics:\n{topic_list}\n\n"
            "Output numbered RESEARCH QUEUE (max 8 steps). Prioritize deep research + hooks.",
            context=ctx,
        )

    def run_full_research(self, topic: str, *, user_request: str = "") -> list[UnderlingResult]:
        """Full research stack on one topic — deep → competitor → hooks → trends."""
        results: list[UnderlingResult] = []
        ai_video = user_wants_ai_video_research(user_request)
        ctx = ai_video_context_block() if ai_video else NICHE_POSITIONING[:800]
        mode = "ai_video" if ai_video else "shorts"

        # Quick scout brief (fast Gemini)
        scout = self.scout.execute(f"Topic: {topic}", context=ctx)
        results.append(scout)

        # Pipeline deep research (web + trends + competitors + cache)
        deep = self.deep.execute(
            topic,
            context=user_request,
            force_refresh=ai_video,
            research_mode=mode,
        )
        results.append(deep)

        research_ctx = deep.detail[:3500]
        competitors = "\n".join(deep.artifacts.get("hooks", []))
        if deep.artifacts.get("research_file"):
            research_ctx += f"\nSaved: {deep.artifacts['research_file']}"

        comp = self.competitor.execute(
            f"Topic: {topic}\n\nResearch:\n{research_ctx}",
            context=ctx,
        )
        results.append(comp)

        hooks = self.hooks.execute(
            f"Topic: {topic}\n\nHooks from research:\n{competitors}\n\nFull context:\n{research_ctx[:2000]}",
            context=ctx,
        )
        results.append(hooks)

        trends = self.trends.execute(topic, context=ctx)
        results.append(trends)

        return results

    def run_deep_only(
        self,
        topic: str,
        *,
        force_refresh: bool = False,
        user_request: str = "",
    ) -> UnderlingResult:
        ai_video = user_wants_ai_video_research(user_request)
        return self.deep.execute(
            topic,
            force_refresh=force_refresh or ai_video,
            research_mode="ai_video" if ai_video else "shorts",
        )

    def run_batch_deep(
        self,
        topics: list[str],
        *,
        deadline: Callable[[], bool],
    ) -> list[UnderlingResult]:
        """Deep research on as many topics as fit before deadline."""
        out: list[UnderlingResult] = []
        for topic in topics:
            if deadline():
                break
            self._progress(f"batch deep: {topic[:50]}")
            out.append(self.deep.execute(topic))
        return out
