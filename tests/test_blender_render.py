"""Blender 3D pipeline — clip paths and config."""

from __future__ import annotations

from pathlib import Path

from shorts_bot.production.render_blender import blender_clip_paths


def test_blender_clip_paths():
    paths = blender_clip_paths(Path("/tmp/clips"), 3)
    assert paths[0].name == "blender_part_01.mp4"
    assert paths[2].name == "blender_part_03.mp4"


def test_blender_config_defaults():
    from shorts_bot.config import Settings

    fields = Settings.model_fields
    assert fields["blender_clips_per_short"].default == 3
    assert fields["blender_clip_seconds"].default == 10.0
    assert fields["blender_samples"].default == 32
    assert fields["blender_timeout_sec"].default == 900


def test_uses_blender_video_property():
    from shorts_bot.config import Settings

    s = Settings(video_backend="blender")
    assert s.uses_blender_video is True
    assert s.uses_kling_video is False


def test_skip_narrator_tts_for_blender(monkeypatch):
    from shorts_bot.config import Settings
    from shorts_bot.production import launch_phase

    monkeypatch.setattr(launch_phase, "settings", Settings(video_backend="blender"))
    assert launch_phase.skip_narrator_tts(99) is True
    assert launch_phase.skip_transcript_sync(99) is True
