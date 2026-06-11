from pathlib import Path
from unittest.mock import patch

from shorts_bot.production.screen_text_overlay import (
    render_overlay_rgba,
    save_overlay_png,
)
from shorts_bot.production.screen_text_spec import ScreenTextOverlay


def test_render_phone_alert_png_has_pixels(tmp_path):
    spec = ScreenTextOverlay(
        kind="phone_alert",
        primary="Motion Detected",
        secondary="Hallway Camera",
        time_label="3:12 AM",
    )
    path = save_overlay_png(spec, tmp_path / "phone.png")
    assert path.exists() and path.stat().st_size > 500
    img = render_overlay_rgba(spec)
    # non-transparent pixels in phone zone
    px = img.getpixel((400, 400))
    assert px[3] > 0


def test_apply_overlay_runs_ffmpeg(tmp_path):
    from shorts_bot.production.screen_text_overlay import apply_overlay_to_video

    vid = tmp_path / "in.mp4"
    vid.write_bytes(b"x")
    png = tmp_path / "ov.png"
    save_overlay_png(
        ScreenTextOverlay(kind="cctv_hud", primary="REC", secondary="3:12 AM"),
        png,
    )
    out = tmp_path / "out.mp4"
    with patch("shorts_bot.production.screen_text_overlay.subprocess.run") as run:
        apply_overlay_to_video(vid, png, out)
        assert run.called
        cmd = run.call_args[0][0]
        assert "overlay" in " ".join(cmd)
