from pathlib import Path

from shorts_bot.__version__ import __version__
from shorts_bot.discord_bot.prefs import briefing_user_ids, remember_dm_user
from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.memory.store import MemoryStore


def test_version_string():
    assert __version__


def test_discord_prefs_remember(tmp_path: Path, monkeypatch):
    import shorts_bot.discord_bot.prefs as prefs

    monkeypatch.setattr(prefs, "PREFS_PATH", tmp_path / "discord_prefs.json")
    remember_dm_user(987654321012345678)
    ids = briefing_user_ids()
    assert "987654321012345678" in ids


def test_improvement_dedupe_by_title(tmp_path: Path):
    mem = MemoryExtensions(MemoryStore(tmp_path / "d.db"))
    a = mem.create_improvement(
        title="Tighten hooks",
        category="hook",
        description="x",
        pros=["a"],
        cons=["b"],
    )
    b = mem.create_improvement(
        title="tighten hooks",
        category="hook",
        description="y",
        pros=["c"],
        cons=["d"],
    )
    assert a.id == b.id
    assert len(mem.list_improvements(status="pending")) == 1


def test_health_has_version():
    from fastapi.testclient import TestClient
    from shorts_bot.web.app import app

    r = TestClient(app).get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert "version" in data
    assert "pending_improvements" in data
