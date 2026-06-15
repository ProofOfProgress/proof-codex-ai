"""Reflect hook for Blender RL best trial."""

from __future__ import annotations

from shorts_bot.learning.reflect import reflect_after_blender_rl
from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.memory.store import MemoryStore
from shorts_bot.production.blender.params import BlenderParams


def test_reflect_after_blender_rl_writes_applied_params(tmp_path, monkeypatch):
    monkeypatch.setattr("shorts_bot.learning.reflect.settings.self_training_enabled", True)

    store = MemoryStore(tmp_path / "t.db")
    mem = MemoryExtensions(store)
    out = reflect_after_blender_rl(
        mem,
        draft_id=2,
        score=8.1,
        passed=True,
        params=BlenderParams(camera_z=2.2, face_scale=1.4),
        issues=[],
    )
    assert out is not None
    assert "Blender self-train" in out
    assert mem.get_training_config("applied:blender-draft-2")
