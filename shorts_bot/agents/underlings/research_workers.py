"""Research underlings — deep research, competitors, hooks, trends."""

from __future__ import annotations

import time

from shorts_bot.agents.roles import (
    COMPETITOR_ANALYST,
    HOOK_ANALYST,
    RESEARCH_SCOUT,
    TRENDS_SCOUT,
)
from shorts_bot.agents.underlings.base import Underling, UnderlingResult
from shorts_bot.config import settings


class ResearchScoutUnderling(Underling):
    role = RESEARCH_SCOUT
    name = "research_scout"

    def execute(self, task: str, *, context: str = "") -> UnderlingResult:
        t0 = time.monotonic()
        self._progress(f"scouting {task[:50]}…")
        detail = self._gemini(task, context=context)
        return UnderlingResult(
            underling=self.name,
            task="scout_brief",
            summary=f"Scout brief: {task[:60]}",
            detail=detail,
            elapsed_seconds=time.monotonic() - t0,
            artifacts={"topic": task},
        )


class DeepResearchUnderling(Underling):
    """Wraps production deep_research_topic — web, trends, competitors, JSON cache."""

    name = "deep_research_worker"

    def execute(
        self,
        topic: str,
        *,
        context: str = "",
        force_refresh: bool = False,
        research_mode: str = "shorts",
    ) -> UnderlingResult:
        t0 = time.monotonic()
        self._progress(f"deep research: {topic[:50]}…")
        from shorts_bot.production.research import deep_research_topic, research_path

        refresh = force_refresh or settings.manager_research_force_refresh
        pr = deep_research_topic(topic, force_refresh=refresh, research_mode=research_mode)
        path = research_path(topic)
        detail = pr.draft_context()
        if pr.competitor_titles:
            detail += "\n\nCompetitor titles:\n" + "\n".join(f"- {t}" for t in pr.competitor_titles[:8])
        if pr.recommended_path:
            detail += f"\n\nPath: {pr.recommended_path}"

        return UnderlingResult(
            underling=self.name,
            task="deep_research",
            summary=f"Deep research: {topic[:70]}",
            detail=detail,
            elapsed_seconds=time.monotonic() - t0,
            artifacts={
                "topic": topic,
                "research_file": str(path),
                "hooks": pr.hook_angles[:5],
                "force_refresh": refresh,
                "sources": pr.research_sources,
            },
        )


class CompetitorAnalystUnderling(Underling):
    role = COMPETITOR_ANALYST
    name = "competitor_analyst"

    def execute(self, task: str, *, context: str = "") -> UnderlingResult:
        t0 = time.monotonic()
        self._progress("analysing competitor gap…")
        detail = self._gemini(task, context=context)
        return UnderlingResult(
            underling=self.name,
            task="competitor_analysis",
            summary="Competitor gap analysis",
            detail=detail,
            elapsed_seconds=time.monotonic() - t0,
        )


class HookAnalystUnderling(Underling):
    role = HOOK_ANALYST
    name = "hook_analyst"

    def execute(self, task: str, *, context: str = "") -> UnderlingResult:
        t0 = time.monotonic()
        self._progress("ranking hooks…")
        detail = self._gemini(task, context=context)
        return UnderlingResult(
            underling=self.name,
            task="hook_analysis",
            summary="Hook ranking + title variants",
            detail=detail,
            elapsed_seconds=time.monotonic() - t0,
        )


class TrendsScoutUnderling(Underling):
    role = TRENDS_SCOUT
    name = "trends_scout"

    def execute(self, task: str, *, context: str = "") -> UnderlingResult:
        t0 = time.monotonic()
        self._progress("checking trend signals…")
        trends_block = ""
        try:
            from shorts_bot.research.google_trends import fetch_google_trends

            trends = fetch_google_trends(task)
            if trends:
                trends_block = trends.context_block()
        except Exception as exc:
            trends_block = f"(trends fetch skipped: {exc})"

        detail = self._gemini(
            f"Topic cluster: {task}\n\nTrend data:\n{trends_block or '(none)'}",
            context=context,
        )
        return UnderlingResult(
            underling=self.name,
            task="trends_scan",
            summary=f"Trends scan: {task[:50]}",
            detail=detail,
            elapsed_seconds=time.monotonic() - t0,
        )
