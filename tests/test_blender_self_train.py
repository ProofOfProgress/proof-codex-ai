"""Blender self-reinforcement — params, trials, issue patches."""

from __future__ import annotations

from pathlib import Path

from shorts_bot.production.blender.params import (
    BlenderParams,
    patch_from_issues,
    save_params,
)
from shorts_bot.production.blender.trials import BlenderTrial, BlenderTrialStore


def test_patch_from_issues_boosts_mouth_on_red_feedback():
    p = BlenderParams(mouth_emissive=5.0, mouth_red=0.9)
    out = patch_from_issues(p, ["mouth interior not red enough", "needs blood"])
    assert out.mouth_emissive > p.mouth_emissive
    assert out.mouth_red >= p.mouth_red


def test_patch_from_issues_raises_camera_on_low_angle():
    p = BlenderParams(camera_z=2.0)
    out = patch_from_issues(p, ["camera too low angle"])
    assert out.camera_z > p.camera_z


def test_params_clamp_bounds():
    p = BlenderParams(samples=999, face_scale=3.0, camera_z=0.5).clamp()
    assert p.samples <= 64
    assert p.face_scale <= 1.85
    assert p.camera_z >= 2.5


def test_trial_store_keeps_best(tmp_path: Path):
    store = BlenderTrialStore(tmp_path / "draft_2")
    store.record(
        BlenderTrial(
            trial_id=1,
            params=BlenderParams(),
            score=6.0,
            passed=False,
        )
    )
    store.record(
        BlenderTrial(
            trial_id=2,
            params=BlenderParams(face_scale=1.5),
            score=8.2,
            passed=True,
        )
    )
    best = store.best()
    assert best is not None
    assert best.trial_id == 2
    assert store.best_path.is_file()


def test_save_and_load_params_roundtrip(tmp_path: Path):
    path = tmp_path / "best_params.json"
    p = BlenderParams(camera_z=2.9, mouth_emissive=9.0)
    save_params(path, p, meta={"score": 8.0})
    loaded = __import__(
        "shorts_bot.production.blender.params", fromlist=["load_params"]
    ).load_params(path)
    assert loaded is not None
    assert loaded.camera_z == 2.9
    assert loaded.mouth_emissive == 9.0
