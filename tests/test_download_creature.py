"""Auto-download SCP-096 creature model."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from shorts_bot.production.blender.creature_paths import resolve_creature_model
from shorts_bot.production.blender.download_creature import (
    ATTRIBUTION_TEXT,
    ensure_scp096_model,
)


def test_ensure_scp096_skips_when_glb_present(tmp_path: Path, monkeypatch):
    creature_dir = tmp_path / "scp_096"
    creature_dir.mkdir()
    glb = creature_dir / "scp_096.glb"
    glb.write_bytes(b"x" * 12000)

    monkeypatch.setattr(
        "shorts_bot.production.blender.download_creature.SCP096_DIR",
        creature_dir,
    )
    monkeypatch.setattr(
        "shorts_bot.production.blender.creature_paths.SCP096_DIR",
        creature_dir,
    )

    with patch("shorts_bot.production.blender.download_creature._download") as dl:
        hit = ensure_scp096_model()
        dl.assert_not_called()
    assert hit == glb


def test_attribution_mentions_license():
    assert "Creative Commons" in ATTRIBUTION_TEXT
    assert "Jabka666" in ATTRIBUTION_TEXT
