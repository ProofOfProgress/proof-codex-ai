"""Composited diegetic UI text — all phone UI drawn inside the device screen."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from shorts_bot.production.framing import FRAME_HEIGHT, FRAME_WIDTH
from shorts_bot.production.screen_text_spec import ScreenTextOverlay

# POV phone in hands — centered lower-mid (matches I2V clips)
_PHONE_X, _PHONE_Y, _PHONE_W, _PHONE_H = 140, 300, 800, 1180
_GIBBERISH_SCRUB = (380, 1580, 700, 340)


@dataclass(frozen=True)
class PhoneLayout:
    x: int
    y: int
    w: int
    h: int

    @property
    def screen(self) -> tuple[int, int, int, int]:
        """Inner display rect (inset from bezel)."""
        inset_x, inset_y = 28, 72
        return (
            self.x + inset_x,
            self.y + inset_y,
            self.w - inset_x * 2,
            self.h - inset_y - 36,
        )


def phone_layout(*, width: int = FRAME_WIDTH, height: int = FRAME_HEIGHT) -> PhoneLayout:
    return PhoneLayout(_PHONE_X, _PHONE_Y, _PHONE_W, _PHONE_H)


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


def normalize_overlay_spec(spec: ScreenTextOverlay) -> ScreenTextOverlay:
    """Legacy phone_alert → in-phone feed states (no floating frame pop-ups)."""
    if spec.kind != "phone_alert":
        return spec
    primary_lower = spec.primary.lower()
    if "live audio" in primary_lower or "tap" in primary_lower:
        state = "live_audio"
    elif "opening" in primary_lower:
        state = "app_opening"
    elif "motion" in primary_lower:
        state = "motion_banner"
    else:
        state = "app_opening"
    return ScreenTextOverlay(
        kind="phone_feed",
        primary=spec.primary,
        secondary=spec.secondary,
        tertiary=spec.tertiary,
        time_label=spec.time_label,
        accent=spec.accent,
        feed_state=state,
    )


def scrub_regions_for_spec(spec: ScreenTextOverlay | None) -> list[tuple[int, int, int, int, float]]:
    gx, gy, gw, gh = _GIBBERISH_SCRUB
    regions: list[tuple[int, int, int, int, float]] = [(gx, gy, gw, gh, 0.94)]
    if spec is None:
        return regions
    norm = normalize_overlay_spec(spec) if spec else None
    if norm and norm.kind in {"phone_feed", "message_bubble"}:
        lay = phone_layout()
        regions.append((lay.x, lay.y, lay.w, lay.h, 0.93))
    if norm and norm.kind == "cctv_hud":
        regions.append((FRAME_WIDTH - 400, 1520, 400, 360, 0.85))
    return regions


def _scrub_vf_chain(spec: ScreenTextOverlay | None) -> str:
    parts: list[str] = []
    for x, y, w, h, alpha in scrub_regions_for_spec(spec):
        parts.append(f"drawbox=x={x}:y={y}:w={w}:h={h}:color=black@{alpha}:t=fill")
    return ",".join(parts)


def _is_phone_overlay(spec: ScreenTextOverlay) -> bool:
    norm = normalize_overlay_spec(spec)
    return norm.kind in {"phone_feed", "message_bubble"}


def render_overlay_rgba(
    spec: ScreenTextOverlay,
    *,
    width: int = FRAME_WIDTH,
    height: int = FRAME_HEIGHT,
) -> "Image.Image":
    from PIL import Image, ImageDraw

    spec = normalize_overlay_spec(spec)
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    if spec.kind == "phone_feed":
        _draw_phone_device(draw, spec, width=width, height=height)
    elif spec.kind == "cctv_hud":
        _draw_cctv_hud(draw, spec, width=width, height=height)
    elif spec.kind == "message_bubble":
        _draw_phone_message(draw, spec, width=width, height=height)
    elif spec.kind == "motion_chip":
        _draw_cctv_hud(
            draw,
            ScreenTextOverlay(
                kind="cctv_hud",
                primary="REC",
                secondary=spec.secondary,
                tertiary=spec.primary,
                accent=spec.accent,
            ),
            width=width,
            height=height,
        )

    return canvas


def _draw_phone_chassis(draw, lay: PhoneLayout) -> tuple[int, int, int, int]:
    px, py, pw, ph = lay.x, lay.y, lay.w, lay.h
    draw.rounded_rectangle(
        [px, py, px + pw, py + ph],
        radius=52,
        fill=(10, 10, 12, 255),
        outline=(55, 55, 60, 255),
        width=5,
    )
    sx, sy, sw, sh = lay.screen
    draw.rounded_rectangle(
        [sx, sy, sx + sw, sy + sh],
        radius=28,
        fill=(4, 4, 6, 255),
    )
    # Dynamic island / notch inside bezel only
    notch_w, notch_h = 180, 34
    nx = px + pw // 2 - notch_w // 2
    draw.rounded_rectangle(
        [nx, py + 16, nx + notch_w, py + 16 + notch_h],
        radius=17,
        fill=(0, 0, 0, 255),
    )
    return sx, sy, sw, sh


def _draw_inscreen_status_bar(draw, sx: int, sy: int, sw: int, time_lbl: str) -> int:
    """Status row inside the phone screen — returns y below bar."""
    draw.text((sx + 16, sy + 8), time_lbl or "3:12 AM", fill="#EBEBF5", font=_font(18))
    draw.text((sx + sw - 72, sy + 8), "5G", fill="#EBEBF5", font=_font(16, bold=True))
    draw.rectangle([sx + 8, sy + 36, sx + sw - 8, sy + 38], fill=(40, 40, 44, 255))
    return sy + 44


def _draw_security_app_header(draw, sx: int, y: int, sw: int, accent: str) -> int:
    draw.rounded_rectangle(
        [sx + 12, y, sx + 52, y + 40],
        radius=10,
        fill=accent,
    )
    draw.text((sx + 64, y + 4), "Security", fill="#FFFFFF", font=_font(24, bold=True))
    draw.text((sx + 64, y + 32), "Home", fill="#8E8E93", font=_font(16))
    return y + 56


def _draw_inscreen_banner(
    draw,
    sx: int,
    sy: int,
    sw: int,
    *,
    title: str,
    subtitle: str,
    accent: str,
    y: int,
) -> None:
    """Notification banner INSIDE the phone display — not floating on the frame."""
    bh = 88
    draw.rounded_rectangle(
        [sx + 12, y, sx + sw - 12, y + bh],
        radius=16,
        fill=(22, 22, 26, 245),
        outline=(60, 60, 66, 255),
        width=2,
    )
    draw.rounded_rectangle(
        [sx + 24, y + 14, sx + 56, y + 46],
        radius=8,
        fill=accent,
    )
    draw.text((sx + 68, y + 12), title[:28], fill="#FFFFFF", font=_font(20, bold=True))
    draw.text((sx + 68, y + 40), subtitle[:36], fill="#AEAEB2", font=_font(17))


def _draw_hallway_feed(
    draw,
    sx: int,
    sy: int,
    sw: int,
    sh: int,
    *,
    with_figure: bool,
    green: str,
    time_lbl: str,
    label: str,
) -> None:
    draw.rectangle([sx, sy, sx + sw, sy + sh], fill=(6, 16, 11, 255))
    mid_x = sx + sw // 2
    floor_y = sy + sh - 16
    draw.polygon(
        [(mid_x, sy + 60), (sx + 12, floor_y), (sx + sw - 12, floor_y)],
        fill=(10, 26, 16, 255),
    )
    draw.line([(mid_x, sy + 60), (mid_x, floor_y)], fill=(24, 60, 34, 200), width=2)
    door_w = 64
    draw.rectangle(
        [mid_x - door_w // 2, sy + 100, mid_x + door_w // 2, floor_y - 50],
        fill=(36, 48, 38, 255),
    )
    if with_figure:
        fig_w, fig_h = 72, 200
        fx = mid_x - fig_w // 2
        fy = floor_y - fig_h - 30
        draw.rectangle([fx, fy, fx + fig_w, fy + fig_h], fill=(2, 6, 4, 255))
        draw.ellipse([fx + 14, fy - 42, fx + 58, fy], fill=(2, 6, 4, 255))
    for ly in range(sy, sy + sh, 5):
        draw.line([(sx, ly), (sx + sw, ly)], fill=(0, 0, 0, 22), width=1)
    draw.text((sx + 12, sy + 8), "REC", fill=green, font=_font(18, bold=True))
    draw.text((sx + sw - 100, sy + 8), time_lbl, fill=green, font=_font(16, bold=True))
    if label:
        draw.text((sx + 12, sy + sh - 28), label, fill=green, font=_font(16, bold=True))


def _draw_phone_device(draw, spec: ScreenTextOverlay, *, width: int, height: int) -> None:
    lay = phone_layout(width=width, height=height)
    sx, sy, sw, sh = _draw_phone_chassis(draw, lay)
    time_lbl = spec.time_label or spec.secondary or "3:12 AM"
    green = spec.accent
    state = spec.feed_state or "empty"

    if state == "app_opening":
        y = _draw_inscreen_status_bar(draw, sx, sy, sw, time_lbl)
        y = _draw_security_app_header(draw, sx, y + 8, sw, spec.accent)
        _draw_inscreen_banner(
            draw,
            sx,
            sy,
            sw,
            title=spec.primary or "Opening Security…",
            subtitle=spec.secondary or "Hallway Camera",
            accent=spec.accent,
            y=y + 12,
        )
        draw.text((sx + sw // 2 - 40, sy + sh - 80), "Loading feed…", fill="#636366", font=_font(18))
        return

    if state == "live_audio":
        feed_top = _draw_inscreen_status_bar(draw, sx, sy, sw, time_lbl)
        feed_h = sh - (feed_top - sy) - 100
        _draw_hallway_feed(
            draw,
            sx,
            feed_top,
            sw,
            feed_h,
            with_figure=False,
            green=green,
            time_lbl=time_lbl,
            label="LIVE",
        )
        _draw_inscreen_banner(
            draw,
            sx,
            sy,
            sw,
            title="Live Audio",
            subtitle=spec.secondary or "Tap detected",
            accent=spec.accent,
            y=sy + sh - 92,
        )
        return

    if state == "motion_banner":
        feed_top = _draw_inscreen_status_bar(draw, sx, sy, sw, time_lbl)
        y = _draw_security_app_header(draw, sx, feed_top + 4, sw, "#FF453A")
        _draw_inscreen_banner(
            draw,
            sx,
            sy,
            sw,
            title=spec.primary or "Motion Detected",
            subtitle=spec.secondary or "Hallway Camera",
            accent="#FF453A",
            y=y + 4,
        )
        feed_top2 = y + 100
        feed_h = sy + sh - feed_top2 - 8
        _draw_hallway_feed(
            draw,
            sx,
            feed_top2,
            sw,
            feed_h,
            with_figure=False,
            green=green,
            time_lbl=time_lbl,
            label="LIVE",
        )
        return

    # Camera feed states (empty / figure closer)
    feed_top = _draw_inscreen_status_bar(draw, sx, sy, sw, time_lbl)
    _draw_hallway_feed(
        draw,
        sx,
        feed_top,
        sw,
        sh - (feed_top - sy),
        with_figure=state == "figure_closer",
        green=green,
        time_lbl=time_lbl,
        label=spec.tertiary or ("MOTION" if state == "figure_closer" else "LIVE"),
    )


def _draw_phone_message(draw, spec: ScreenTextOverlay, *, width: int, height: int) -> None:
    lay = phone_layout(width=width, height=height)
    sx, sy, sw, sh = _draw_phone_chassis(draw, lay)
    y = _draw_inscreen_status_bar(draw, sx, sy, sw, spec.secondary or "3:12 AM")
    text = spec.primary
    font = _font(26)
    lines = [text[i : i + 24] for i in range(0, len(text), 24)][:3]
    line_h = 34
    bh = 24 + len(lines) * line_h + 20
    by = y + 20
    draw.rounded_rectangle(
        [sx + 16, by, sx + sw - 16, by + bh],
        radius=20,
        fill=(48, 48, 52, 250),
    )
    ty = by + 16
    for ln in lines:
        draw.text((sx + 28, ty), ln, fill="#FFFFFF", font=font)
        ty += line_h


def _draw_cctv_hud(draw, spec: ScreenTextOverlay, *, width: int, height: int) -> None:
    green = spec.accent
    font_sm = _font(24, bold=True)
    font_lg = _font(30, bold=True)
    for y in range(0, height, 8):
        draw.line([(0, y), (width, y)], fill=(0, 0, 0, 10), width=1)
    draw.text((48, 56), spec.primary, fill=green, font=font_lg)
    draw.text((width - 200, 56), spec.secondary, fill=green, font=font_sm)
    if spec.tertiary:
        draw.text((48, 100), spec.tertiary, fill=green, font=font_sm)


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
    if spec is not None and _is_phone_overlay(spec):
        vf = (
            f"[0:v]{scrub},gblur=sigma=12,eq=brightness=-0.1:saturation=0.75[scrub];"
            f"[scrub][1:v]overlay=0:0:format=auto[out]"
        )
    else:
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
    out = tmp_dir / f"screen_text_{segment_index:03d}.mp4"
    if spec is None:
        apply_caption_scrub_only(clip_path, out)
        return out
    norm = normalize_overlay_spec(spec)
    png = tmp_dir / f"screen_text_{segment_index:03d}.png"
    save_overlay_png(norm, png)
    apply_overlay_to_video(clip_path, png, out, spec=norm)
    return out


def overlay_top_safe(spec: ScreenTextOverlay) -> bool:
    """True when phone UI has no trophy pop-ups floating above the device bezel."""
    norm = normalize_overlay_spec(spec)
    if norm.kind != "phone_feed":
        return True
    lay = phone_layout()
    img = render_overlay_rgba(norm)
    for y in range(0, max(0, lay.y - 4)):
        for x in range(0, FRAME_WIDTH, 6):
            if img.getpixel((x, y))[3] > 40:
                return False
    return True
