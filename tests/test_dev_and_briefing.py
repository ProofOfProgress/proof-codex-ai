from pathlib import Path

from shorts_bot.briefing.builder import build_morning_briefing
from shorts_bot.config import settings
from shorts_bot.learning.learned_file import LearnedFile
from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.memory.store import MemoryStore


def test_dev_task_flow(tmp_path: Path):
    mem = MemoryExtensions(MemoryStore(tmp_path / "d.db"))
    task = mem.create_dev_task(title="Polish UI", description="Make dashboard prettier")
    assert task.status == "pending"
    approved = mem.review_dev_task(task.id, approved=True, note="Yes")
    assert approved.status == "approved"
    pending = mem.list_dev_tasks(status="pending")
    assert all(t.id != task.id for t in pending)


def test_dev_auto_approval_stays_on_top_four(tmp_path: Path):
    from shorts_bot.automation.auto_approve import dev_task_is_auto_approvable

    mem = MemoryExtensions(MemoryStore(tmp_path / "auto.db"))
    polish = mem.create_dev_task(title="Polish UI", description="Make dashboard prettier")
    upload = mem.create_dev_task(
        title="Improve upload QC",
        description="Block weak vision QC before YouTube publish",
    )

    assert dev_task_is_auto_approvable(polish) is False
    assert dev_task_is_auto_approvable(upload) is True


def test_learned_file_append(tmp_path: Path):
    path = tmp_path / "LEARNED.md"
    lf = LearnedFile(path)
    from shorts_bot.memory.extensions import Improvement

    imp = Improvement(
        id=1,
        title="Tighten hooks",
        category="hook",
        description="Start with curiosity gap",
        pros=["a"],
        cons=["b"],
        status="approved",
        source="test",
        created_at="now",
        reviewed_at="now",
        review_note="",
    )
    lf.record_improvement(imp, approved=True)
    text = path.read_text(encoding="utf-8")
    assert "Tighten hooks" in text


def test_morning_briefing_contains_essentials():
    text = build_morning_briefing()
    assert "Peripheral" in text
    assert "localhost" in text
    assert "TOMORROW" in text or "YouTube" in text


def test_config_no_discord_settings():
    assert not hasattr(settings, "has_discord")
