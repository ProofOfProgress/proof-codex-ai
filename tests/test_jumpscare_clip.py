from pathlib import Path
from unittest.mock import patch

from shorts_bot.config import Settings
from shorts_bot.production.jumpscare_clip import (
    jumpscare_clip_is_valid,
    scare_play_and_setup_durations,
    trim_jumpscare_impact,
)


def test_scare_play_and_setup_durations():
    setup, play = scare_play_and_setup_durations(4.2)
    assert play >= 1.0
    assert setup >= 0.9
    assert abs((setup + play) - 4.2) < 0.01


def test_jumpscare_dedicated_clip_config_defaults():
    fields = Settings.model_fields
    assert fields["jumpscare_dedicated_clip"].default is True
    assert fields["jumpscare_auto_generate"].default is True
    assert fields["jumpscare_clip_play_seconds"].default == 2.2


def test_jumpscare_clip_is_valid_requires_hailuo_meta(tmp_path):
    clips = tmp_path / "clips"
    clips.mkdir()
    (clips / "jumpscare_lunge.mp4").write_bytes(b"x" * 20_000)
    assert not jumpscare_clip_is_valid(tmp_path, clips)
    (tmp_path / "jumpscare_clip.json").write_text(
        '{"model": "minimax/hailuo-2.3-fast", "clip_file": "jumpscare_lunge.mp4"}',
        encoding="utf-8",
    )
    assert jumpscare_clip_is_valid(tmp_path, clips)


def test_trim_jumpscare_impact_runs_ffmpeg(tmp_path):
    src = tmp_path / "src.mp4"
    src.write_bytes(b"x")
    dest = tmp_path / "scare.mp4"
    with patch("shorts_bot.production.jumpscare_clip.probe_clip_duration", return_value=6.0):
        with patch("shorts_bot.production.jumpscare_clip.subprocess.run") as run:
            trim_jumpscare_impact(src, dest, play_seconds=1.8, width=1080, height=1920)
            assert run.called
            cmd = run.call_args[0][0]
            assert "ffmpeg" in cmd[0]
            assert "-ss" in cmd


def test_compose_finale_jumpscare_segment(tmp_path):
    from shorts_bot.production.jumpscare_clip import compose_finale_jumpscare_segment

    still = tmp_path / "00.24.png"
    still.write_bytes(b"png")
    scare_src = tmp_path / "jumpscare_lunge.mp4"
    scare_src.write_bytes(b"x")
    dest = tmp_path / "finale.mp4"

    with patch("shorts_bot.production.jumpscare_clip.probe_clip_duration", return_value=5.0):
        with patch("shorts_bot.production.jumpscare_clip.trim_setup_hold") as setup:
            with patch("shorts_bot.production.jumpscare_clip.trim_jumpscare_impact") as scare:
                with patch("shorts_bot.production.jumpscare_clip.concat_clips") as concat:
                    compose_finale_jumpscare_segment(
                        jumpscare_src=scare_src,
                        dest=dest,
                        segment_duration=4.0,
                        setup_still=still,
                        setup_clip=None,
                        width=1080,
                        height=1920,
                    )
                    setup.assert_called_once()
                    scare.assert_called_once()
                    concat.assert_called_once()
