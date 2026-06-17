"""Tests for natural-language Blender motion prompts."""

from __future__ import annotations

import json
from pathlib import Path

from shorts_bot.production.blender.motion_prompt import (
    PHASE_DEFAULT_PROMPTS,
    _procedural_keyframes,
    _sanitize_keyframes,
    generate_motion_keyframes,
    load_beat_prompt,
    motion_cache_path,
    resolve_backend,
)


def test_procedural_wave_keyframes():
    kf = _procedural_keyframes("wave")
    assert len(kf) >= 5
    assert any("Bone_007" in frame["bones"] for frame in kf)


def test_sanitize_keyframes():
    raw = {
        "keyframes": [
            {"t": 0.0, "bones": {"Bone_007": [0, 0, 0], "BAD": [9, 9, 9]}},
            {"t": 1.0, "bones": {"Bone_007": [-2.0, 0.1, 0.0]}},
        ]
    }
    out = _sanitize_keyframes(raw, phase="wave")
    assert len(out) == 2
    assert "BAD" not in out[1]["bones"]


def test_load_beat_prompt_draft_2():
    prompt = load_beat_prompt(2, "wave")
    assert "wave" in prompt.lower() or "arm" in prompt.lower()


def test_generate_motion_procedural():
    payload = generate_motion_keyframes("test wave", phase="wave", backend="procedural")
    assert payload["backend"] == "procedural"
    assert len(payload["keyframes"]) >= 2


def test_motion_cache_path():
    p = motion_cache_path(Path("/tmp/pack"), "wave")
    assert p.name == "motion_wave.json"


def test_resolve_backend_offline(monkeypatch):
    from shorts_bot.config import settings

    monkeypatch.setattr(settings, "blender_motion_backend", "auto")
    monkeypatch.setattr(settings, "gemini_api_key", None)
    monkeypatch.setattr(settings, "openai_api_key", None)
    assert resolve_backend() == "procedural"


def test_prepare_motion_json_roundtrip(tmp_path):
    from shorts_bot.production.blender.motion_prompt import prepare_motion_for_pack

    pack = tmp_path / "draft_99"
    paths = prepare_motion_for_pack(pack, 99, phases=("wave",), force=True)
    assert paths["wave"].is_file()
    data = json.loads(paths["wave"].read_text())
    assert data["phase"] == "wave"
    assert data["keyframes"]


def test_phase_defaults_exist():
    for phase in ("open", "wave", "lunge"):
        assert phase in PHASE_DEFAULT_PROMPTS
