from pathlib import Path

from fastapi.testclient import TestClient

from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.memory.store import MemoryStore
from shorts_bot.services.ops import BotOperations
from shorts_bot.web.app import app


def test_checklist_api():
    r = TestClient(app).get("/api/checklist")
    assert r.status_code == 200
    items = r.json()["items"]
    assert any(i["id"] == "web" for i in items)
    assert not any(i["id"] == "discord" for i in items)


def test_briefing_api():
    r = TestClient(app).get("/api/briefing")
    assert r.status_code == 200
    assert "briefing" in r.json()
    assert "Peripheral" in r.json()["briefing"]


def test_ops_dev_chat_routing():
    ops = BotOperations()
    msg = ops.chat("dev: Test feature | do something cool")
    assert "Dev task" in msg


def test_ops_pending_command():
    msg = BotOperations().chat("pending")
    assert "caught up" in msg.lower() or "yes" in msg.lower()


def test_dev_task_dedupe(tmp_path: Path):
    mem = MemoryExtensions(MemoryStore(tmp_path / "x.db"))
    a = mem.create_dev_task(title="Fix bug", description="a")
    b = mem.create_dev_task(title="fix bug", description="b")
    assert a.id == b.id
