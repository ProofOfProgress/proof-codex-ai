from pathlib import Path
from unittest.mock import patch

from shorts_bot.production.screen_text_overlay import (
    normalize_overlay_spec,
    overlay_top_safe,
    render_overlay_rgba,
    save_overlay_png,
)
from shorts_bot.production.screen_text_spec import ScreenTextOverlay


def test_legacy_phone_alert_maps_to_in_phone_feed():
    spec = ScreenTextOverlay(
        kind="phone_alert",
        primary="Opening Security…",
        secondary="Hallway Camera",
        time_label="3:12 AM",
    )
    norm = normalize_overlay_spec(spec)
    assert norm.kind == "phone_feed"
    assert norm.feed_state == "app_opening"


def test_phone_ui_not_in_top_quarter_of_frame():
    for state in ("app_opening", "live_audio", "empty", "figure_closer", "motion_banner"):
        spec = ScreenTextOverlay(
            kind="phone_feed",
            primary="Security",
            secondary="Hallway Camera",
            time_label="3:12 AM",
            feed_state=state,
        )
        assert overlay_top_safe(spec), state


def test_render_phone_feed_png_has_pixels_in_device_zone(tmp_path):
    from shorts_bot.production.screen_text_overlay import phone_layout

    spec = ScreenTextOverlay(
        kind="phone_feed",
        primary="Hallway Camera",
        secondary="3:12 AM",
        feed_state="app_opening",
    )
    path = save_overlay_png(spec, tmp_path / "phone.png")
    assert path.exists() and path.stat().st_size > 500
    img = render_overlay_rgba(spec)
    lay = phone_layout()
    sx, sy, _, _ = lay.screen
    assert img.getpixel((sx + 40, sy + 80))[3] > 0


def test_screen_only_overlay_png_is_screen_sized(tmp_path):
    from shorts_bot.production.screen_text_overlay import (
        phone_layout,
        render_screen_overlay_rgba,
    )

    spec = ScreenTextOverlay(
        kind="phone_feed",
        primary="Hallway Camera",
        secondary="3:12 AM",
        feed_state="empty",
    )
    lay = phone_layout()
    _, _, sw, sh = lay.screen
    screen_img = render_screen_overlay_rgba(spec)
    assert screen_img.size == (sw, sh)


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
