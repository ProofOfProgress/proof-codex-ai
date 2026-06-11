"""Composited diegetic UI text — crisp phone/CCTV overlays burned onto clips."""

from __future__ import annotations

import subprocess
from pathlib import Path

from shorts_bot.production.framing import FRAME_HEIGHT, FRAME_WIDTH
from shorts_bot.production.screen_text_spec import ScreenTextOverlay

# Phone screen bounds in 9:16 (POV holding phone)
_PHONE_X, _PHONE_Y, _PHONE_W, _PHONE_H = 200, 360, 680, 1040
# Bottom band — AI models often paint gibberish here; captions burn above later
_CAPTION_SCRUB_Y, _CAPTION_SCRUB_H = 1480, 440


def _font(size: int, *, bold: bool = False):
    from PIL import ImageFont

    names = (
        ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
        if bold
        else ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    )
    names.append("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    for path in names:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def scrub_regions_for_spec(spec: ScreenTextOverlay | None) -> list[tuple[int, int, int, int, float]]:
    """Return drawbox regions (x, y, w, h, alpha) to kill AI gibberish before overlay."""
    regions: list[tuple[int, int, int, int, float]] = [
        (0, _CAPTION_SCRUB_Y, FRAME_WIDTH, _CAPTION_SCRUB_H, 0.96),
    ]
    if spec is None:
        return regions
    kind = spec.kind
    if kind in {"phone_alert", "phone_feed", "message_bubble"}:
        regions.append((_PHONE_X, _PHONE_Y, _PHONE_W, _PHONE_H, 0.92))
    if kind == "cctv_hud":
        regions.append((FRAME_WIDTH - 360, _CAPTION_SCRUB_Y - 80, 360, 200, 0.88))
    return regions


def _scrub_vf_chain(spec: ScreenTextOverlay | None) -> str:
    parts: list[str] = []
    for x, y, w, h, alpha in scrub_regions_for_spec(spec):
        parts.append(
            f"drawbox=x={x}:y={y}:w={w}:h={h}:color=black@{alpha}:t=fill"
        )
    return ",".join(parts)


def render_overlay_rgba(
    spec: ScreenTextOverlay,
    *,
    width: int = FRAME_WIDTH,
    height: int = FRAME_HEIGHT,
) -> "Image.Image":
    from PIL import Image, ImageDraw

    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    if spec.kind == "phone_alert":
        _draw_phone_alert(draw, spec, width=width, height=height)
    elif spec.kind == "cctv_hud":
        _draw_cctv_hud(draw, spec, width=width, height=height)
    elif spec.kind == "message_bubble":
        _draw_message_bubble(draw, spec, width=width, height=height)
    elif spec.kind == "motion_chip":
        _draw_motion_chip(draw, spec, width=width, height=height)
    elif spec.kind == "phone_feed":
        _draw_phone_feed(draw, spec, width=width, height=height)

    return canvas


def _draw_phone_alert(draw, spec: ScreenTextOverlay, *, width: int, height: int) -> None:
    """iOS-style notification card — upper safe zone."""
    px, py, pw, ph = 120, 140, 840, 300
    draw.rounded_rectangle(
        [px, py, px + pw, py + ph],
        radius=36,
        fill=(12, 12, 14, 235),
        outline=(48, 48, 52, 255),
        width=3,
    )
    draw.text((px + 32, py + 24), spec.time_label or "3:12 AM", fill="#EBEBF5", font=_font(24))
    draw.rounded_rectangle(
        [px + 32, py + 72, px + 80, py + 120],
        radius=12,
        fill=spec.accent,
    )
    draw.text((px + 96, py + 78), "Security", fill="#FFFFFF", font=_font(26, bold=True))
    draw.text((px + 96, py + 112), "now", fill="#8E8E93", font=_font(20))
    draw.text((px + 32, py + 148), spec.primary, fill="#FFFFFF", font=_font(32, bold=True))
    draw.text((px + 32, py + 192), spec.secondary, fill="#AEAEB2", font=_font(26))


def _draw_phone_feed(draw, spec: ScreenTextOverlay, *, width: int, height: int) -> None:
    """Replace phone screen with clean night-vision feed + corner HUD."""
    px, py, pw, ph = _PHONE_X, _PHONE_Y, _PHONE_W, _PHONE_H
    green = spec.accent
    # phone bezel
    draw.rounded_rectangle(
        [px - 12, py - 12, px + pw + 12, py + ph + 12],
        radius=40,
        fill=(6, 6, 8, 255),
        outline=(40, 40, 44, 255),
        width=4,
    )
    sx, sy, sw, sh = px + 20, py + 56, pw - 40, ph - 120
    draw.rectangle([sx, sy, sx + sw, sy + sh], fill=(8, 22, 16, 255))
    # hallway perspective
    mid_x = sx + sw // 2
    draw.polygon(
        [(mid_x, sy + 40), (sx + 30, sy + sh - 20), (sx + sw - 30, sy + sh - 20)],
        fill=(12, 32, 22, 255),
    )
    draw.line([(mid_x, sy + 40), (mid_x, sy + sh - 20)], fill=(20, 50, 30, 200), width=3)
    if spec.feed_state == "figure_closer":
        fig_w, fig_h = 90, 260
        fx = mid_x - fig_w // 2
        fy = sy + sh - fig_h - 60
        draw.rectangle([fx, fy, fx + fig_w, fy + fig_h], fill=(4, 8, 6, 255))
        draw.ellipse([fx + 20, fy - 50, fx + 70, fy], fill=(4, 8, 6, 255))
    # HUD on feed
    draw.text((sx + 16, sy + 16), "REC", fill=green, font=_font(22, bold=True))
    draw.text((sx + sw - 130, sy + 16), spec.secondary or "3:12 AM", fill=green, font=_font(20, bold=True))
    if spec.tertiary:
        draw.text((sx + 16, sy + sh - 44), spec.tertiary, fill=green, font=_font(18, bold=True))
    if spec.feed_state == "figure_closer" and spec.tertiary:
        chip = spec.tertiary
        draw.rounded_rectangle(
            [sx + sw - 150, sy + 52, sx + sw - 16, sy + 88],
            radius=8,
            fill=(0, 0, 0, 180),
            outline=green,
            width=1,
        )
        draw.text((sx + sw - 140, sy + 58), chip, fill=green, font=_font(18, bold=True))


def _draw_cctv_hud(draw, spec: ScreenTextOverlay, *, width: int, height: int) -> None:
    """Night-vision timestamp + REC — corners only, no reticle."""
    green = spec.accent
    font_sm = _font(26, bold=True)
    font_lg = _font(32, bold=True)
    for y in range(0, height, 8):
        draw.line([(0, y), (width, y)], fill=(0, 0, 0, 12), width=1)
    draw.text((48, 56), spec.primary, fill=green, font=font_lg)
    draw.text((width - 200, 56), spec.secondary, fill=green, font=font_sm)
    if spec.tertiary:
        draw.text((48, 108), spec.tertiary, fill=green, font=font_sm)


def _draw_message_bubble(draw, spec: ScreenTextOverlay, *, width: int, height: int) -> None:
    px, py, pw = 180, 200, 720
    text = spec.primary
    font = _font(32)
    lines = [text[i : i + 28] for i in range(0, len(text), 28)][:2]
    line_h = 40
    bh = 36 + len(lines) * line_h + 28
    draw.rounded_rectangle(
        [px, py, px + pw, py + bh],
        radius=28,
        fill=(48, 48, 52, 240),
    )
    y = py + 24
    for ln in lines:
        draw.text((px + 28, y), ln, fill="#FFFFFF", font=font)
        y += line_h


def _draw_motion_chip(draw, spec: ScreenTextOverlay, *, width: int, height: int) -> None:
    """Legacy — prefer phone_feed; kept for cached manifests."""
    legacy = ScreenTextOverlay(
        kind="cctv_hud",
        primary="REC",
        secondary=spec.secondary,
        tertiary=spec.primary,
        accent=spec.accent,
    )
    green = legacy.accent
    font_sm = _font(26, bold=True)
    font_lg = _font(32, bold=True)
    draw.text((48, 56), legacy.primary, fill=green, font=font_lg)
    draw.text((width - 200, 56), legacy.secondary, fill=green, font=font_sm)
    if legacy.tertiary:
        draw.text((48, 108), legacy.tertiary, fill=green, font=font_sm)


def save_overlay_png(spec: ScreenTextOverlay, path: Path) -> Path:
    from PIL import Image

    img = render_overlay_rgba(spec)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "PNG")
    return path


def apply_overlay_to_video(
    video_path: Path,
    overlay_png: Path,
    dest: Path,
    *,
    spec: ScreenTextOverlay | None = None,
) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    scrub = _scrub_vf_chain(spec)
    vf = f"[0:v]{scrub}[scrub];[scrub][1:v]overlay=0:0:format=auto[out]"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video_path.resolve()),
            "-i",
            str(overlay_png.resolve()),
            "-filter_complex",
            vf,
            "-map",
            "[out]",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-pix_fmt",
            "yuv420p",
            str(dest),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return dest


def apply_caption_scrub_only(video_path: Path, dest: Path) -> Path:
    """Scrub bottom gibberish band even when no UI overlay."""
    scrub = _scrub_vf_chain(None)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video_path.resolve()),
            "-vf",
            scrub,
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-pix_fmt",
            "yuv420p",
            str(dest),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return dest


def maybe_apply_screen_text(
    clip_path: Path,
    spec: ScreenTextOverlay | None,
    *,
    tmp_dir: Path,
    segment_index: int,
) -> Path:
    """Scrub AI gibberish zones, then composite crisp UI."""
    out = tmp_dir / f"screen_text_{segment_index:03d}.mp4"
    if spec is None:
        apply_caption_scrub_only(clip_path, out)
        return out
    png = tmp_dir / f"screen_text_{segment_index:03d}.png"
    save_overlay_png(spec, png)
    apply_overlay_to_video(clip_path, png, out, spec=spec)
    return out
