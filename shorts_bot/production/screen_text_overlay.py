"""Composited diegetic UI text — crisp phone/CCTV overlays burned onto clips."""

from __future__ import annotations

import subprocess
from pathlib import Path

from shorts_bot.production.framing import FRAME_HEIGHT, FRAME_WIDTH
from shorts_bot.production.screen_text_spec import ScreenTextOverlay


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


def _text_center(draw, text: str, font, x0: int, y: int, x1: int, fill: str) -> None:
    if hasattr(draw, "textlength"):
        tw = draw.textlength(text, font=font)
    else:
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
    x = x0 + (x1 - x0 - tw) / 2
    draw.text((x, y), text, fill=fill, font=font)


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

    return canvas


def _draw_phone_alert(draw, spec: ScreenTextOverlay, *, width: int, height: int) -> None:
    """iOS-style notification card in upper phone zone."""
    px, py, pw, ph = 200, 260, 680, 520
    draw.rounded_rectangle(
        [px, py, px + pw, py + ph],
        radius=48,
        fill=(12, 12, 14, 235),
        outline=(48, 48, 52, 255),
        width=3,
    )
    # status bar
    draw.text((px + 36, py + 28), spec.time_label or "3:12 AM", fill="#EBEBF5", font=_font(26))
    # app row
    draw.rounded_rectangle(
        [px + 36, py + 88, px + 92, py + 144],
        radius=14,
        fill=spec.accent,
    )
    draw.text((px + 110, py + 96), "Security", fill="#FFFFFF", font=_font(28, bold=True))
    draw.text((px + 110, py + 132), "now", fill="#8E8E93", font=_font(22))
    # alert body
    draw.text((px + 36, py + 190), spec.primary, fill="#FFFFFF", font=_font(34, bold=True))
    draw.text((px + 36, py + 238), spec.secondary, fill="#AEAEB2", font=_font(28))
    if spec.tertiary:
        draw.text((px + 36, py + 280), spec.tertiary, fill="#636366", font=_font(24))


def _draw_cctv_hud(draw, spec: ScreenTextOverlay, *, width: int, height: int) -> None:
    """Night-vision timestamp + REC — corners, mute-safe."""
    green = spec.accent
    font_sm = _font(28, bold=True)
    font_lg = _font(36, bold=True)
    # scanlines subtle
    for y in range(0, height, 6):
        draw.line([(0, y), (width, y)], fill=(0, 0, 0, 18), width=1)
    draw.text((48, 52), spec.primary, fill=green, font=font_lg)
    draw.text((width - 320, 52), spec.secondary, fill=green, font=font_sm)
    if spec.tertiary:
        draw.text((48, height - 120), spec.tertiary, fill=green, font=font_sm)
    # motion reticle box
    bx, by, bw, bh = width // 2 - 80, int(height * 0.42), 160, 220
    draw.rectangle([bx, by, bx + bw, by + bh], outline=green, width=2)


def _draw_message_bubble(draw, spec: ScreenTextOverlay, *, width: int, height: int) -> None:
    """iMessage-style delivered bubble — upper phone zone."""
    px, py, pw = 180, 320, 720
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
    if spec.secondary:
        draw.text((px + 28, py + bh + 12), spec.secondary, fill="#8E8E93", font=_font(22))


def _draw_motion_chip(draw, spec: ScreenTextOverlay, *, width: int, height: int) -> None:
    """Small motion badge on feed refresh."""
    chip = f"  {spec.primary}  "
    font = _font(26, bold=True)
    if hasattr(draw, "textlength"):
        tw = draw.textlength(chip, font=font)
    else:
        bbox = draw.textbbox((0, 0), chip, font=font)
        tw = bbox[2] - bbox[0]
    x, y = 56, 100
    draw.rounded_rectangle(
        [x, y, x + int(tw) + 24, y + 44],
        radius=10,
        fill=(0, 0, 0, 200),
        outline=spec.accent,
        width=2,
    )
    draw.text((x + 12, y + 8), chip.strip(), fill=spec.accent, font=font)
    if spec.secondary:
        draw.text((width - 280, 100), spec.secondary, fill="#39FF14", font=_font(24, bold=True))


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
) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video_path.resolve()),
            "-i",
            str(overlay_png.resolve()),
            "-filter_complex",
            "[0:v][1:v]overlay=0:0:format=auto[out]",
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


def maybe_apply_screen_text(
    clip_path: Path,
    spec: ScreenTextOverlay | None,
    *,
    tmp_dir: Path,
    segment_index: int,
) -> Path:
    """Apply composited UI if spec present; otherwise return clip unchanged."""
    if spec is None:
        return clip_path
    png = tmp_dir / f"screen_text_{segment_index:03d}.png"
    save_overlay_png(spec, png)
    out = tmp_dir / f"screen_text_{segment_index:03d}.mp4"
    apply_overlay_to_video(clip_path, png, out)
    return out
