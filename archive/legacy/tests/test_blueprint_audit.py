"""Blueprint audit — proves 90-day checklist wiring."""

from pathlib import Path

from shorts_bot.learning.blueprint_audit import audit_score, run_blueprint_audit
from shorts_bot.memory.store import MemoryStore


def test_blueprint_audit_software_passes(tmp_path: Path, monkeypatch):
    from shorts_bot.config import settings

    monkeypatch.setattr(settings, "database_path", tmp_path / "t.db")
    monkeypatch.setattr(settings, "data_dir", Path("data"))
    monkeypatch.setattr(settings, "script_qc_enabled", True)
    monkeypatch.setattr(settings, "run_telemetry_enabled", True)
    monkeypatch.setattr(settings, "mem0_enabled", True)
    monkeypatch.setattr(settings, "invideo_render_retries", 2)
    monkeypatch.setattr(settings, "auto_daily_enabled", False)

    store = MemoryStore(tmp_path / "t.db")
    checks = run_blueprint_audit(store=store)
    passed, total, ops = audit_score(checks)
    assert passed == total
    assert ops == 1  # daily loop paused by design
