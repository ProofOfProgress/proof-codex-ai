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
    assert "PERIPHERAL" in text
    assert "localhost" in text
    assert "TOMORROW" in text or "YouTube" in text


def test_config_discord_public_key_property():
    assert hasattr(settings, "discord_public_key")
    assert hasattr(settings, "has_discord")
