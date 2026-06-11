from pathlib import Path

from shorts_bot.automation.auto_approve import dev_task_is_auto_approvable, improvement_is_auto_approvable
from shorts_bot.automation.coordinator import auto_approve_pending_improvements
from shorts_bot.config import settings
from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.memory.store import MemoryStore


def _mem(tmp_path: Path) -> MemoryExtensions:
    return MemoryExtensions(MemoryStore(tmp_path / "auto.db"))


def test_auto_approve_hook_improvement(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(settings, "auto_approve_improvements", True)
    mem = _mem(tmp_path)
    imp = mem.create_improvement(
        title="Tighten hook",
        category="hook",
        description="Rewrite hooks with curiosity in first line.",
        pros=["Fast test"],
        cons=["May overdo it"],
        source="reward:punish:Video 1",
    )
    assert improvement_is_auto_approvable(imp)
    n = auto_approve_pending_improvements(mem)
    assert n == 1
    assert mem.get_improvement(imp.id).status == "approved"
    assert mem.applied_improvements()


def test_skip_risky_improvement(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(settings, "auto_approve_improvements", True)
    mem = _mem(tmp_path)
    imp = mem.create_improvement(
        title="Change niche",
        category="strategy",
        description="Pivot channel to login-heavy oauth flow.",
        pros=["x"],
        cons=["y"],
        source="reward:punish:Video 2",
    )
    assert not improvement_is_auto_approvable(imp)
    assert auto_approve_pending_improvements(mem) == 0


def test_dev_task_blocks_login(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(settings, "auto_approve_dev_tasks", True)
    mem = _mem(tmp_path)
    task = mem.create_dev_task(
        title="OAuth login",
        description="Set up Google OAuth login flow in browser",
    )
    assert not dev_task_is_auto_approvable(task)


def test_schedule_publish_due(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(settings, "auto_publish_hours", 24)
    mem = _mem(tmp_path)
    mem.schedule_publish(video_id="abc123", draft_id=1, publish_after_hours=0)
    # publish_after_hours=0 should no-op in schedule_publish
    due = mem.list_due_scheduled_publishes()
    assert due == []
