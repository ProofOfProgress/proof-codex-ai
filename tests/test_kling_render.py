"""Kling 2×15s pipeline — script split, prompts, clip paths."""

from __future__ import annotations

from shorts_bot.production.render_kling import (
    build_kling_multi_prompt,
    build_kling_prompt,
    kling_clip_paths,
    split_script_parts,
)


def test_split_script_two_parts():
    parts = split_script_parts(
        "They all stared at the wall.",
        "I woke up screaming. The villager smiled wrong. "
        "You dreamed again, didn't you? I ran. The Eye was behind my eyelids.",
        parts=2,
    )
    assert len(parts) == 2
    assert "stared" in parts[0]
    assert "Eyelids" in parts[1] or "eyelids" in parts[1].lower()


def test_build_kling_prompt_first_person():
    prompt = build_kling_prompt(
        "village eye dream",
        'I whisper: "Why is everyone staring?"',
        part_index=0,
        total_parts=2,
    )
    assert "9:16" in prompt
    assert "First-person" in prompt or "first-person" in prompt.lower()
    assert "village eye dream" in prompt


def test_multi_prompt_durations_sum():
    shots = build_kling_multi_prompt(
        "Line one. Line two. Line three. Line four.",
        total_seconds=15,
    )
    assert len(shots) >= 1
    assert sum(s["duration"] for s in shots) == 15


def test_kling_clip_paths():
    from pathlib import Path

    paths = kling_clip_paths(Path("/tmp/clips"), 2)
    assert paths[0].name == "kling_part_01.mp4"
    assert paths[1].name == "kling_part_02.mp4"


def test_kling_config_defaults():
    from shorts_bot.config import Settings

    fields = Settings.model_fields
    assert fields["video_backend"].default == "kling"
    assert fields["kling_provider"].default == "official"
    assert fields["kling_model"].default == "kling-v2-6"
    assert fields["kling_clips_per_short"].default == 3
    assert fields["kling_generate_audio"].default is True
    assert fields["kling_skip_narrator_tts"].default is True
    assert fields["ai_video_max_beats"].default == 2


def test_uses_kling_native_audio_property():
    from shorts_bot.config import Settings

    s = Settings(
        video_backend="kling",
        kling_generate_audio=True,
        kling_skip_narrator_tts=True,
    )
    assert s.uses_kling_video is True
    assert s.uses_kling_native_audio is True

    legacy = Settings(video_backend="legacy_i2v")
    assert legacy.uses_kling_native_audio is False
