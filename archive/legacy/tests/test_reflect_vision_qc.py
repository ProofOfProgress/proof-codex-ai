"""Vision QC → self-learning avoid rules."""

from __future__ import annotations

from shorts_bot.learning.reflect import reflect_after_vision_qc, vision_qc_snapshot
from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.memory.store import MemoryStore


def test_reflect_after_vision_qc_writes_avoid_rule(tmp_path, monkeypatch):
    monkeypatch.setattr("shorts_bot.learning.reflect.settings.self_training_enabled", True)

    store = MemoryStore(tmp_path / "t.db")
    mem = MemoryExtensions(store)
    out = reflect_after_vision_qc(
        mem,
        draft_id=7,
        topic="afternoon energy crash",
        score=4.5,
        passed=False,
        issues=["frozen frame at 0:12", "text unreadable"],
    )
    assert out is not None
    assert "Vision QC failed" in out
    assert mem.get_training_config("avoid:vision-afternoon-energy-crash")
    assert "frozen frame" in mem.get_training_config("avoid:vision-afternoon-energy-crash")


def test_reflect_after_vision_qc_skips_when_passed(tmp_path, monkeypatch):
    monkeypatch.setattr("shorts_bot.learning.reflect.settings.self_training_enabled", True)

    store = MemoryStore(tmp_path / "t.db")
    mem = MemoryExtensions(store)
    assert (
        reflect_after_vision_qc(
            mem,
            draft_id=1,
            topic="sleep",
            score=8.0,
            passed=True,
            issues=[],
        )
        is None
    )


def test_vision_qc_snapshot_shape():
    snap = vision_qc_snapshot(score=7.5, passed=True, issues=["a"], warnings=["b"])
    assert snap["score"] == 7.5
    assert snap["passed"] is True
    assert snap["issues"] == ["a"]
