"""Tests for Module 6 motion-enhanced pan loop."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from shorts_bot.tiktok_shop.video_variants import (
    build_motion_enhance_vf,
    mean_inter_frame_motion,
)


def test_build_motion_enhance_vf_has_lateral_and_shake():
    vf = build_motion_enhance_vf(lateral_amplitude=0.12, micro_shake_px=4.0)
    assert "sin(2*PI*t/5)" in vf
    assert "sin(2*PI*t*8)" in vf
    assert "crop=" in vf


def test_mean_inter_frame_motion_static_vs_changed(tmp_path: Path):
    a = tmp_path / "a.jpg"
    b = tmp_path / "b.jpg"
    c = tmp_path / "c.jpg"
    Image.new("RGB", (540, 960), (10, 10, 10)).save(a, format="JPEG", quality=90)
    Image.new("RGB", (540, 960), (10, 10, 10)).save(b, format="JPEG", quality=90)
    Image.new("RGB", (540, 960), (200, 50, 50)).save(c, format="JPEG", quality=90)
    static_score = mean_inter_frame_motion([a, b])
    motion_score = mean_inter_frame_motion([a, c])
    assert static_score < 0.001
    assert motion_score > 0.05
