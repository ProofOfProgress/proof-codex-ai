"""Motion backend — procedural default, Mixamo opt-in."""

from __future__ import annotations

import os

from shorts_bot.config import settings


def test_procedural_default_without_mixamo():
    os.environ.pop("BLENDER_MOTION_BACKEND", None)
    os.environ.pop("BLENDER_USE_MIXAMO", None)
    from shorts_bot.production.blender.motion_backend import motion_env, use_downloaded_motion

    assert settings.blender_use_mixamo_motion is False
    assert use_downloaded_motion() is False
    assert motion_env()["BLENDER_MOTION_BACKEND"] == "procedural"


def test_mixamo_only_when_opt_in(monkeypatch):
    monkeypatch.setenv("BLENDER_MOTION_BACKEND", "proscenium_fbx")
    from shorts_bot.production.blender.motion_backend import use_downloaded_motion

    assert use_downloaded_motion() is True


def test_auto_respects_use_mixamo_flag(monkeypatch):
    monkeypatch.setenv("BLENDER_MOTION_BACKEND", "auto")
    monkeypatch.setenv("BLENDER_USE_MIXAMO", "0")
    from shorts_bot.production.blender.motion_backend import use_downloaded_motion

    assert use_downloaded_motion() is False
