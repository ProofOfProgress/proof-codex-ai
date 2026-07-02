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
    assert "color=black" not in vf
    assert "force_original_aspect_ratio=increase" in vf


def test_loop_clip_has_no_black_pillarbox_bars():
    """Integration — regen loop must not add black side bars (coach/Gemini ban risk)."""
    from pathlib import Path

    from shorts_bot.tiktok_shop.module1_qc import _extract_frame

    clip = Path("data/tiktok_shop/clips/bur_bur_mermaid_brush_loop.mp4")
    if not clip.is_file():
        import pytest

        pytest.skip("dry-run clip not on disk")

    out = clip.parent / "_test_frame_letterbox.jpg"
    _extract_frame(clip, 2.5, out)
    from PIL import Image

    im = Image.open(out).convert("RGB")
    w, h = im.size

    def edge_brightness(x0: int, x1: int) -> float:
        strip = im.crop((x0, 0, x1, h))
        pixels = list(strip.getdata())
        return sum(sum(p) for p in pixels) / len(pixels) / 3

    left = edge_brightness(0, w // 20)
    right = edge_brightness(w - w // 20, w)
    center = edge_brightness(w // 3, 2 * w // 3)
    assert left > 40 and right > 40, f"black pillarbox detected L={left:.0f} R={right:.0f}"
    assert center > 40
    out.unlink(missing_ok=True)


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
