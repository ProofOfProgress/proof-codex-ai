from pathlib import Path

from shorts_bot.learning.workflow import (
    StepResult,
    WorkflowDefinition,
    WorkflowRun,
    WorkflowStep,
    load_active_workflow,
    load_seed_workflow,
    save_active_workflow,
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
    assert "youtube_upload" in ids


def test_active_workflow_persists(tmp_path: Path):
    store = MemoryStore(tmp_path / "t.db")
    wf = load_active_workflow(store)
    assert wf.id == "daily_invideo"
    wf2 = load_active_workflow(store)
    assert wf2.version == wf.version


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
        step_results=[
            StepResult("invideo_render", False, "expect_download timed out after 2400s"),
        ],
    )
    result = evolve_after_daily_run(store, run, memory=mem)
    after_wf = load_active_workflow(store)
    after = after_wf.step("invideo_render").params["wait_render_sec"]
    assert after == before + 600
    assert after_wf.version == wf.version + 1
    assert result.applied


def test_evolve_rotates_hook_on_punish(tmp_path: Path):
    store = MemoryStore(tmp_path / "t.db")
    mem = MemoryExtensions(store)
    wf = load_active_workflow(store)
    before = wf.step("build_brief").params["hook_template"]

    reward = RewardResult(
        video_label="ChatGPT Plus review",
        score=0.2,
        verdict="punish",
        reason="High swipe-away on hook",
        diagnosis="Hook failed to stop scroll",
        metrics={"viewed_vs_swiped_away": 80},
    )
    result = evolve_from_rewards(mem, [reward])
    after_wf = load_active_workflow(store)
    after = after_wf.step("build_brief").params["hook_template"]
    assert after != before
    assert result.applied


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
    recent = rs.recent(limit=1)
    assert len(recent) == 1
    assert recent[0]["draft_id"] == 3
    assert rs.step_failure_streak("invideo_render") == 1
