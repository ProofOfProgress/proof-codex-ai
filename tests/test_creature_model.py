"""Creature model path resolution."""

from __future__ import annotations

from pathlib import Path

from shorts_bot.production.blender.creature_paths import (
    SCP096_DIR,
    resolve_creature_model,
)


def test_resolve_creature_model_missing():
    assert resolve_creature_model("/nonexistent/model.fbx") is None


def test_resolve_creature_model_explicit_file(tmp_path: Path):
    fbx = tmp_path / "monster.fbx"
    fbx.write_bytes(b"fake")
    assert resolve_creature_model(fbx) == fbx


def test_scp096_dir_constant():
    assert "scp_096" in str(SCP096_DIR)
