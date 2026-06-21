"""Tests for system upgrade batch."""

from pathlib import Path

from shorts_bot.learning.owner_signals import capture_owner_signal
from shorts_bot.learning.run_telemetry import record_run, recent_runs, telemetry_path
from shorts_bot.learning.script_qc import score_script_brief
from shorts_bot.learning.workflow import WorkflowRun, StepResult
from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.memory.store import MemoryStore
from shorts_bot.production.product_queue import load_product_queue, next_queue_item


def test_product_queue_loads():
    q = load_product_queue(Path("data/product_queue.json"))
    assert len(q) >= 10
    assert q[0].product


def test_next_queue_item(tmp_path: Path):
    store = MemoryStore(tmp_path / "t.db")
    item = next_queue_item(store)
    assert item is not None
    assert item.hook


def test_script_qc_offline_passes():
    from shorts_bot.config import settings

    brief = (
        "ChatGPT Plus costs $20. Verdict: Skip unless you hit limits daily. "
        "Pay only if you use GPT-4 every day."
    )
    r = score_script_brief(
        product="ChatGPT Plus",
        hook="Everyone's paying for ChatGPT Plus — worth it?",
        brief=brief,
        verdict_hint="Skip unless daily power user",
    )
    assert r.score >= 5


def test_owner_signal_avoid(tmp_path: Path):
    mem = MemoryExtensions(MemoryStore(tmp_path / "t.db"))
    msg = capture_owner_signal(mem, "The framing was wonky on that last video — avoid tight zoom opens")
    assert msg and "avoid" in msg.lower()


def test_telemetry_jsonl(tmp_path: Path, monkeypatch):
    from shorts_bot.config import settings

    monkeypatch.setattr(settings, "data_dir", tmp_path)
    monkeypatch.setattr(settings, "run_telemetry_enabled", True)
    run = WorkflowRun(
        workflow_id="daily_invideo",
        workflow_version=1,
        draft_id=1,
        topic="Test",
        ok=False,
        step_results=[StepResult("script_qc", False, "low score")],
    )
    record_run(run, evolution_summary="test")
    assert telemetry_path().is_file()
    assert recent_runs(1)[0]["topic"] == "Test"
