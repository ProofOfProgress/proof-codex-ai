from pathlib import Path

from fastapi.testclient import TestClient

from shorts_bot.discord_bot.prefs import briefing_user_ids, remember_dm_user
from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.memory.store import MemoryStore
from shorts_bot.services.ops import BotOperations
from shorts_bot.web.app import app


def test_checklist_api():
    r = TestClient(app).get("/api/checklist")
    assert r.status_code == 200
    items = r.json()["items"]
    assert any(i["id"] == "discord" for i in items)


def test_ops_dev_chat_routing():
    ops = BotOperations()
    msg = ops.chat("dev: Test feature | do something cool")
    assert "Dev task" in msg


def test_ops_pending_command():
    msg = BotOperations().chat("pending")
    assert "caught up" in msg.lower() or "yes" in msg.lower()


def test_multi_dm_users_briefing(tmp_path: Path, monkeypatch):
    import shorts_bot.discord_bot.prefs as prefs

    monkeypatch.setattr(prefs, "PREFS_PATH", tmp_path / "p.json")
    monkeypatch.setattr(prefs.settings, "discord_owner_id", None)
    monkeypatch.setattr(prefs.settings, "discord_notify_ids", "")
    remember_dm_user(111)
    remember_dm_user(222)
    ids = briefing_user_ids()
    assert "111" in ids and "222" in ids


def test_dev_task_dedupe(tmp_path: Path):
    mem = MemoryExtensions(MemoryStore(tmp_path / "x.db"))
    a = mem.create_dev_task(title="Fix bug", description="a")
    b = mem.create_dev_task(title="fix bug", description="b")
    assert a.id == b.id
