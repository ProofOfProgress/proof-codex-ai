"""Evolve daily-loop workflow steps from run outcomes + YouTube rewards."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from shorts_bot.config import settings
from shorts_bot.learning.workflow import (
    HOOK_TEMPLATES,
    WorkflowDefinition,
    WorkflowRun,
    bump_workflow_version,
    load_active_workflow,
    save_active_workflow,
    set_step_param,
)
from shorts_bot.learning.workflow_store import WorkflowRunStore
from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.memory.store import MemoryStore
from shorts_bot.rewards.engine import RewardResult

_CREDIT_FAIL = re.compile(r"\b(credit|upgrade|paywall|subscription|payment)\b", re.I)
_RENDER_TIMEOUT = re.compile(r"\b(timeout|timed out|expect_download)\b", re.I)


@dataclass
class EvolutionResult:
    applied: list[str]
    proposals: list[str]

    def summary(self) -> str:
        parts = []
        if self.applied:
            parts.append("Applied: " + "; ".join(self.applied))
        if self.proposals:
            parts.append("Proposed: " + "; ".join(self.proposals))
        return " | ".join(parts) if parts else "No workflow changes"


def _next_hook_template(current: str) -> str:
    pool = list(HOOK_TEMPLATES)
    if current in pool:
        idx = pool.index(current)
        return pool[(idx + 1) % len(pool)]
    return pool[0]


def evolve_after_daily_run(
    store: MemoryStore,
    run: WorkflowRun,
    *,
    memory: MemoryExtensions | None = None,
) -> EvolutionResult:
    """Tune safe params after each daily tick; propose structural changes when risky."""
    if not settings.workflow_evolution_enabled:
        return EvolutionResult([], [])

    wf = load_active_workflow(store)
    run_store = WorkflowRunStore(store)
    run_store.record(run)

    applied: list[str] = []
    proposals: list[str] = []
    render = _step(run, "invideo_render")

    if render and not render.ok:
        detail = render.detail
        if _CREDIT_FAIL.search(detail):
            proposals.append(
                "Add Drive-link fetch fallback before upload when InVideo credits exhausted"
            )
            if memory:
                memory.create_improvement(
                    title="Daily loop: Drive fetch fallback after InVideo paywall",
                    category="workflow",
                    description=(
                        "When invideo_render fails with credits/paywall, skip re-generate and "
                        "wait for owner Drive link → fetch_url_cli → upload. Reduces wasted ticks."
                    ),
                    pros=[
                        "Keeps daily loop alive without new InVideo credits",
                        "Matches broken-phone handoff workflow",
                    ],
                    cons=[
                        "Needs owner to export MP4 once per video until credits return",
                        "Not fully hands-off until credits restored",
                    ],
                    source="workflow:invideo_credit_fail",
                )
        elif _RENDER_TIMEOUT.search(detail):
            step = wf.step("invideo_render")
            current = int((step.params if step else {}).get("wait_render_sec", 2400))
            new_wait = min(current + 600, 5400)
            if new_wait > current:
                wf = bump_workflow_version(
                    set_step_param(wf, "invideo_render", "wait_render_sec", new_wait),
                    note=f"render wait {current}→{new_wait}s after timeout",
                )
                save_active_workflow(store, wf)
                applied.append(f"invideo_render wait_render_sec={new_wait}")

    streak = run_store.step_failure_streak("invideo_render", limit=3)
    if streak >= 2 and render and not render.ok:
        proposals.append(f"invideo_render failed {streak} runs in a row — review InVideo login/credits")

    if applied or proposals:
        run.mutation_notes.extend(applied + proposals)

    return EvolutionResult(applied=applied, proposals=proposals)


def evolve_from_rewards(
    memory: MemoryExtensions,
    scored: list[RewardResult],
) -> EvolutionResult:
    """After analytics sync — rotate hook template on hook punish; reinforce on reward."""
    if not settings.workflow_evolution_enabled or not scored:
        return EvolutionResult([], [])

    store = memory.store
    wf = load_active_workflow(store)
    applied: list[str] = []
    proposals: list[str] = []

    for reward in scored:
        if reward.verdict == "neutral":
            continue
        blob = f"{reward.reason} {reward.diagnosis}".lower()
        hook_signal = "hook" in blob or "swipe" in blob

        if reward.verdict == "punish" and hook_signal:
            step = wf.step("build_brief")
            current = str((step.params if step else {}).get("hook_template", HOOK_TEMPLATES[0]))
            new_hook = _next_hook_template(current)
            wf = bump_workflow_version(
                set_step_param(wf, "build_brief", "hook_template", new_hook),
                note="hook template rotated after punish",
            )
            save_active_workflow(store, wf)
            applied.append(f"build_brief hook_template rotated")
            memory.record_learning_episode(
                episode_type="workflow_evolve",
                video_label=reward.video_label,
                verdict=reward.verdict,
                score=reward.score,
                reflection=(
                    f"Workflow evolved: hook template changed after hook punish on "
                    f"«{reward.video_label[:80]}». New template: {new_hook[:120]}"
                ),
                active_rules_json=json.dumps(memory.active_rules_snapshot()),
            )

        elif reward.verdict == "reward" and hook_signal:
            step = wf.step("build_brief")
            current = str((step.params if step else {}).get("hook_template", ""))
            if current:
                key = f"repeat:workflow-hook:{current[:80]}"
                memory.set_training_config(key, f"Hook template worked on {reward.video_label[:80]}")
                applied.append("recorded winning hook template")

        elif reward.verdict == "punish" and "retention" in blob:
            proposals.append("Tighten brief structure / verdict pacing in build_brief step")

    return EvolutionResult(applied=applied, proposals=proposals)


def workflow_status(store: MemoryStore) -> str:
    wf = load_active_workflow(store)
    run_store = WorkflowRunStore(store)
    recent = run_store.recent(limit=5)
    lines = [
        f"Workflow {wf.id} v{wf.version}",
        f"Enabled steps: {', '.join(s.id for s in wf.enabled_steps())}",
    ]
    brief = wf.step("build_brief")
    if brief:
        lines.append(f"Hook template: {brief.params.get('hook_template', '')[:100]}")
    render = wf.step("invideo_render")
    if render:
        lines.append(f"Render wait: {render.params.get('wait_render_sec', 2400)}s")
    if recent:
        last = recent[0]
        lines.append(
            f"Last run: draft #{last.get('draft_id')} ok={last.get('ok')} "
            f"({last.get('created_at', '')[:19]})"
        )
    return "\n".join(lines)


def _step(run: WorkflowRun, step_id: str):
    for s in run.step_results:
        if s.step_id == step_id:
            return s
    return None
