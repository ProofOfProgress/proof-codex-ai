"""Micro jumpscare audio — loud bed + creature roar."""

from pathlib import Path

from shorts_bot.production.micro_jumpscare_render import _create_micro_horror_audio


def test_micro_horror_audio_creates_file(tmp_path: Path):
    out = tmp_path / "horror.mp3"
    _create_micro_horror_audio(2.5, 0.42, out)
    assert out.is_file()
    assert out.stat().st_size > 8000
