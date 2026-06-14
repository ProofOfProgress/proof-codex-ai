"""Micro jumpscare audio — loud bed + CC0 premade roar."""

import shutil
from pathlib import Path

import pytest

from shorts_bot.production.micro_jumpscare_render import (
    _create_micro_horror_audio,
    resolve_micro_roar_path,
)


def test_resolve_micro_roar_path_exists():
    path = resolve_micro_roar_path()
    assert path.is_file()
    assert path.suffix.lower() == ".wav"


def test_micro_horror_audio_creates_file(tmp_path: Path, monkeypatch):
    roar_src = resolve_micro_roar_path()
    fake = tmp_path / "roar.wav"
    shutil.copy(roar_src, fake)
    monkeypatch.setattr(
        "shorts_bot.production.micro_jumpscare_render.resolve_micro_roar_path",
        lambda: fake,
    )
    out = tmp_path / "horror.mp3"
    _create_micro_horror_audio(2.5, 0.42, out)
    assert out.is_file()
    assert out.stat().st_size > 8000
