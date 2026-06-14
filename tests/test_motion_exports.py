"""Tests for Proscenium FBX motion export paths."""

from __future__ import annotations

from pathlib import Path

from shorts_bot.production.blender.motion_exports import (
    draft_id_from_pack,
    motion_fbx_candidates,
    resolve_motion_fbx,
)


def test_draft_id_from_pack():
    assert draft_id_from_pack(Path("/tmp/draft_2")) == 2
    assert draft_id_from_pack(Path("/tmp/other")) is None


def test_motion_fbx_candidates_naming():
    names = [p.name for p in motion_fbx_candidates(2, "wave")]
    assert "draft_2_wave.fbx" in names
    assert "draft_2_wave_proscenium.fbx" in names


def test_resolve_motion_fbx_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "shorts_bot.production.blender.motion_exports.motion_exports_dir",
        lambda: tmp_path,
    )
    assert resolve_motion_fbx(2, "wave") is None


def test_resolve_motion_fbx_found(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "shorts_bot.production.blender.motion_exports.motion_exports_dir",
        lambda: tmp_path,
    )
    fbx = tmp_path / "draft_2_wave.fbx"
    fbx.write_bytes(b"x" * 600)
    assert resolve_motion_fbx(2, "wave") == fbx


def test_blender_motion_backend_defaults():
    from shorts_bot.config import Settings

    fields = Settings.model_fields
    assert fields["blender_motion_backend"].default == "procedural"
    assert fields["blender_animation_tool"].default == "proscenium"
