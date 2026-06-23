"""Mem0 + public evolution tests."""

from pathlib import Path
from unittest.mock import patch

from shorts_bot.learning.mem0_bridge import recall_context_block, remember
from shorts_bot.learning.public_evolve import evolve_hook_after_punish, next_hook_template
from shorts_bot.learning.workflow import (
    StepResult,
    WorkflowRun,
    load_active_workflow,
    load_seed_workflow,
)
from shorts_bot.learning.workflow_evolve import evolve_after_daily_run, evolve_from_rewards
from shorts_bot.learning.workflow_store import WorkflowRunStore
from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.memory.store import MemoryStore
from shorts_bot.rewards.engine import RewardResult


def test_seed_workflow_has_daily_steps():
    wf = load_seed_workflow(Path("data/workflows/daily_invideo_v1.json"))
    ids = [s.id for s in wf.enabled_steps()]
    assert "pick_topic" in ids
    assert "invideo_render" in ids


def test_evolve_increases_render_wait_on_timeout(tmp_path: Path):
    store = MemoryStore(tmp_path / "t.db")
    mem = MemoryExtensions(store)
    wf = load_active_workflow(store)
    before = wf.step("invideo_render").params["wait_render_sec"]
    run = WorkflowRun(
        workflow_id=wf.id,
        workflow_version=wf.version,
        draft_id=1,
        topic="ChatGPT Plus",
        ok=False,
        step_results=[StepResult("invideo_render", False, "expect_download timed out after 2400s")],
    )
    result = evolve_after_daily_run(store, run, memory=mem)
    after = load_active_workflow(store).step("invideo_render").params["wait_render_sec"]
    assert after == before + 600
    assert result.applied


def test_evolve_hook_rotate_fallback(tmp_path: Path):
    store = MemoryStore(tmp_path / "t.db")
    mem = MemoryExtensions(store)
    wf = load_active_workflow(store)
    before = wf.step("build_brief").params["hook_template"]
    reward = RewardResult(
        video_label="ChatGPT Plus",
        score=0.2,
        verdict="punish",
        reason="High swipe-away on hook",
        diagnosis="Hook failed",
        metrics={},
    )
    with patch("shorts_bot.learning.public_evolve.optimize_hook_template", return_value=None):
        result = evolve_from_rewards(mem, [reward])
    after = load_active_workflow(store).step("build_brief").params["hook_template"]
    assert after != before
    assert result.applied


def test_mem0_remember_noop_when_disabled(monkeypatch):
    from shorts_bot.config import settings
    from shorts_bot.learning.mem0_bridge import reset_mem0_cache

    monkeypatch.setattr(settings, "mem0_enabled", False)
    reset_mem0_cache()
    assert remember("test memory") is False
    assert recall_context_block() == ""


def test_workflow_run_history(tmp_path: Path):
    store = MemoryStore(tmp_path / "t.db")
    rs = WorkflowRunStore(store)
    run = WorkflowRun(
        workflow_id="daily_invideo",
        workflow_version=1,
        draft_id=3,
        topic="Claude Pro",
        ok=False,
        step_results=[StepResult("invideo_render", False, "Upgrade plan")],
    )
    rs.record(run)
    assert rs.step_failure_streak("invideo_render") == 1


def test_next_hook_template_rotates():
    from shorts_bot.production.hooks import HOOK_TEMPLATES

    a = HOOK_TEMPLATES[0]
    b = next_hook_template(a)
    assert b != a
    assert "{product}" in b


def test_evolve_hook_after_punish_fallback():
    from shorts_bot.production.hooks import HOOK_TEMPLATES

    current = HOOK_TEMPLATES[0]
    with patch("shorts_bot.learning.public_evolve.optimize_hook_template", return_value=None):
        new, method = evolve_hook_after_punish(current, "high swipe-away")
    assert method == "rotate"
    assert new != current
