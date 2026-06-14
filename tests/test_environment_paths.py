"""Tests for gas-station environment path resolution."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from shorts_bot.production.blender.environment_paths import (
    DEFAULT_ENV_DIR,
    resolve_environment_model,
)


def test_resolve_environment_model_fbx_present(tmp_path: Path):
    fbx = tmp_path / "Gas_station" / "Models" / "Gas_station.fbx"
    fbx.parent.mkdir(parents=True)
    fbx.write_bytes(b"x" * 60000)
    hit = resolve_environment_model(tmp_path)
    assert hit == fbx


def test_resolve_environment_model_missing(tmp_path: Path):
    assert resolve_environment_model(tmp_path) is None


def test_default_env_dir_constant():
    assert DEFAULT_ENV_DIR.parts[-2:] == ("environments", "gas_station")
