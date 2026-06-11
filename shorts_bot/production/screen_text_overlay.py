"""Composited diegetic UI — fullscreen CCTV OSD + alarm clock (no phone screens)."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from shorts_bot.production.framing import FRAME_HEIGHT, FRAME_WIDTH
from shorts_bot.production.screen_text_spec import ScreenTextOverlay

# I2V phone display rect — centered POV in regen clips (hands below screen)
# Raised so bottom ~1040px — clears caption band (~1260px anchor)
_SCREEN_X, _SCREEN_Y, _SCREEN_W, _SCREEN_H = 340, 500, 400, 520
_GIBBERISH_SCRUB = (380, 1580, 700, 340)


@dataclass(frozen=True)
class PhoneLayout:
    x: int
    y: int
    w: int
    h: int

    @property
    def screen(self) -> tuple[int, int, int, int]:
        """Inner display rect — equals layout in screen-only mode."""
        from shorts_bot.config import settings

        if settings.screen_text_screen_only:
            return (self.x, self.y, self.w, self.h)
        inset_x, inset_y = 28, 72
        return (
            self.x + inset_x,
            self.y + inset_y,
            self.w - inset_x * 2,
            self.h - inset_y - 36,
        )


def phone_layout(*, width: int = FRAME_WIDTH, height: int = FRAME_HEIGHT) -> PhoneLayout:
    from shorts_bot.config import settings

    if settings.screen_text_screen_only:
        return PhoneLayout(_SCREEN_X, _SCREEN_Y, _SCREEN_W, _SCREEN_H)
    return PhoneLayout(140, 300, 800, 1180)


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


def scrub_regions_for_spec(
    spec: ScreenTextOverlay | None,
    *,
    include_gibberish: bool = True,
) -> list[tuple[int, int, int, int, float]]:
    regions: list[tuple[int, int, int, int, float]] = []
    if include_gibberish:
        gx, gy, gw, gh = _GIBBERISH_SCRUB
        regions.append((gx, gy, gw, gh, 0.94))
    if spec is None:
        return regions
    norm = normalize_overlay_spec(spec)
    if norm and norm.kind in {"phone_feed", "message_bubble"}:
        lay = phone_layout()
        sx, sy, sw, sh = lay.screen
        from shorts_bot.config import settings

        if settings.screen_text_screen_only:
            regions.append((sx, sy, sw, sh, 0.90))
        else:
            regions.append((lay.x, lay.y, lay.w, lay.h, 0.93))
    if norm and norm.kind == "cctv_hud":
        regions.append((36, 148, 300, 108, 0.88))
    return regions


def _scrub_vf_chain(spec: ScreenTextOverlay | None, *, local: bool = False) -> str:
    parts: list[str] = []
    skip_gibberish = spec is not None and _is_phone_overlay(spec)
    if local and spec is not None and _is_phone_overlay(spec):
        from shorts_bot.config import settings

        if settings.screen_text_screen_only:
            return "drawbox=x=0:y=0:w=iw:h=ih:color=black@0.35:t=fill,gblur=sigma=2,eq=brightness=-0.02:saturation=0.92"
    for x, y, w, h, alpha in scrub_regions_for_spec(spec, include_gibberish=not skip_gibberish):
        parts.append(f"drawbox=x={x}:y={y}:w={w}:h={h}:color=black@{alpha}:t=fill")
    return ",".join(parts)


def _is_phone_overlay(spec: ScreenTextOverlay) -> bool:
    from shorts_bot.production.screen_text_spec import phone_screens_enabled

    if not phone_screens_enabled():
        return False
    norm = normalize_overlay_spec(spec)
    return norm.kind in {"phone_feed", "message_bubble"}


def render_overlay_rgba(
    spec: ScreenTextOverlay,
    *,
    width: int = FRAME_WIDTH,
    height: int = FRAME_HEIGHT,
) -> "Image.Image":
    from PIL import Image, ImageDraw

    from shorts_bot.config import settings

    spec = normalize_overlay_spec(spec)
    if settings.screen_text_screen_only and _is_phone_overlay(spec):
        lay = phone_layout(width=width, height=height)
        sx, sy, sw, sh = lay.screen
        canvas = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas)
        if spec.kind == "phone_feed":
            _draw_phone_screen_content(draw, spec, sw=sw, sh=sh)
        elif spec.kind == "message_bubble":
            _draw_message_on_screen(draw, spec, sw=sw, sh=sh)
        full = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        full.paste(canvas, (sx, sy))
        return full

    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    if spec.kind == "phone_feed":
        _draw_phone_device(draw, spec, width=width, height=height)
    elif spec.kind == "cctv_hud":
        _draw_cctv_hud(draw, spec, width=width, height=height)
    elif spec.kind == "alarm_clock":
        _draw_alarm_clock(draw, spec, width=width, height=height)
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


def render_screen_overlay_rgba(spec: ScreenTextOverlay) -> "Image.Image":
    """Screen-sized RGBA for region-local ffmpeg overlay."""
    from PIL import Image, ImageDraw

    spec = normalize_overlay_spec(spec)
    lay = phone_layout()
    _, _, sw, sh = lay.screen
    canvas = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    if spec.kind == "phone_feed":
        _draw_phone_screen_content(draw, spec, sw=sw, sh=sh)
    elif spec.kind == "message_bubble":
        _draw_message_on_screen(draw, spec, sw=sw, sh=sh)
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
    notch_w, notch_h = 180, 34
    nx = px + pw // 2 - notch_w // 2
    draw.rounded_rectangle(
        [nx, py + 16, nx + notch_w, py + 16 + notch_h],
        radius=17,
        fill=(0, 0, 0, 255),
    )
    return sx, sy, sw, sh


def _draw_inscreen_status_bar(draw, sx: int, sy: int, sw: int, time_lbl: str) -> int:
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
    chrome_only: bool = False,
) -> None:
    if chrome_only:
        draw.text((sx + 12, sy + 8), "REC", fill=green, font=_font(18, bold=True))
        draw.text((sx + sw - 100, sy + 8), time_lbl, fill=green, font=_font(16, bold=True))
        if label:
            draw.text((sx + 12, sy + sh - 28), label, fill=green, font=_font(16, bold=True))
        return
    # No full-screen green wash — I2V feed provides night-vision; HUD text only
    hud = "#8EAEFF"
    if label:
        draw.text((sx + 12, sy + sh - 28), label, fill=hud, font=_font(16, bold=True))


def _draw_phone_screen_content(
    draw,
    spec: ScreenTextOverlay,
    *,
    sw: int,
    sh: int,
) -> None:
    """Draw feed UI in local screen coordinates (0,0)–(sw,sh)."""
    time_lbl = spec.time_label or spec.secondary or "3:12 AM"
    green = spec.accent
    state = spec.feed_state or "empty"

    if state == "app_opening":
        y = _draw_inscreen_status_bar(draw, 0, 0, sw, time_lbl)
        feed_top = y + 4
        feed_h = sh - feed_top - 96
        _draw_hallway_feed(
            draw,
            0,
            feed_top,
            sw,
            feed_h,
            with_figure=False,
            green="#8EAEFF",
            time_lbl=time_lbl,
            label="LIVE",
        )
        _draw_inscreen_banner(
            draw,
            0,
            0,
            sw,
            title=spec.primary or "Opening Security…",
            subtitle=spec.secondary or "Hallway Camera",
            accent=spec.accent,
            y=feed_top + 8,
        )
        return

    if state == "live_audio":
        feed_top = _draw_inscreen_status_bar(draw, 0, 0, sw, time_lbl)
        feed_h = sh - feed_top - 100
        _draw_hallway_feed(
            draw,
            0,
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
            0,
            0,
            sw,
            title="Live Audio",
            subtitle=spec.secondary or "Tap detected",
            accent=spec.accent,
            y=sh - 92,
        )
        return

    if state == "motion_banner":
        feed_top = _draw_inscreen_status_bar(draw, 0, 0, sw, time_lbl)
        y = _draw_security_app_header(draw, 0, feed_top + 4, sw, "#FF453A")
        _draw_inscreen_banner(
            draw,
            0,
            0,
            sw,
            title=spec.primary or "Motion Detected",
            subtitle=spec.secondary or "Hallway Camera",
            accent="#FF453A",
            y=y + 4,
        )
        feed_top2 = y + 100
        feed_h = sh - feed_top2 - 8
        _draw_hallway_feed(
            draw,
            0,
            feed_top2,
            sw,
            feed_h,
            with_figure=False,
            green=green,
            time_lbl=time_lbl,
            label="LIVE",
        )
        return

    _draw_hallway_feed(
        draw,
        0,
        0,
        sw,
        sh,
        with_figure=state == "figure_closer",
        green=green,
        time_lbl=time_lbl,
        label=spec.tertiary or ("MOTION" if state == "figure_closer" else "LIVE"),
    )


def _draw_message_on_screen(draw, spec: ScreenTextOverlay, *, sw: int, sh: int) -> None:
    y = _draw_inscreen_status_bar(draw, 0, 0, sw, spec.secondary or "3:12 AM")
    text = spec.primary
    font = _font(26)
    lines = [text[i : i + 24] for i in range(0, len(text), 24)][:3]
    line_h = 34
    bh = 24 + len(lines) * line_h + 20
    by = y + 20
    draw.rounded_rectangle(
        [16, by, sw - 16, by + bh],
        radius=20,
        fill=(48, 48, 52, 250),
    )
    ty = by + 16
    for ln in lines:
        draw.text((28, ty), ln, fill="#FFFFFF", font=font)
        ty += line_h


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


def _draw_alarm_clock(draw, spec: ScreenTextOverlay, *, width: int, height: int) -> None:
    """Digital alarm clock on nightstand — bottom-right, above caption safe zone."""
    time_txt = (spec.primary or spec.time_label or "3:12 AM").strip()
    cx, cy, cw, ch = width - 320, height - 520, 260, 110
    draw.rounded_rectangle(
        [cx, cy, cx + cw, cy + ch],
        radius=12,
        fill=(12, 12, 14, 200),
        outline=(80, 80, 88, 255),
        width=3,
    )
    draw.rounded_rectangle(
        [cx + 10, cy + 10, cx + cw - 10, cy + ch - 10],
        radius=8,
        fill=(4, 4, 6, 230),
    )
    font_lg = _font(42, bold=True)
    font_sm = _font(18)
    tw = time_txt.replace(" AM", "").replace(" PM", "")
    draw.text((cx + 24, cy + 22), tw, fill="#FF453A", font=font_lg)
    ampm = "AM" if "AM" in time_txt.upper() else ("PM" if "PM" in time_txt.upper() else spec.secondary or "")
    if ampm:
        draw.text((cx + cw - 56, cy + 38), ampm, fill="#FF6961", font=font_sm)


def _draw_cctv_hud(draw, spec: ScreenTextOverlay, *, width: int, height: int) -> None:
    """Small night-vision OSD chip — top-left, not full-width floating text."""
    green = spec.accent
    font_sm = _font(20, bold=True)
    font_lg = _font(22, bold=True)
    pad = 14
    box_x, box_y = 36, 148
    box_w, box_h = 300, 108
    draw.rounded_rectangle(
        [box_x, box_y, box_x + box_w, box_y + box_h],
        radius=10,
        fill=(0, 0, 0, 140),
        outline=(57, 255, 20, 80),
        width=2,
    )
    tx, ty = box_x + pad, box_y + pad
    draw.text((tx, ty), spec.primary, fill=green, font=font_lg)
    draw.text((tx, ty + 30), spec.secondary, fill=green, font=font_sm)
    if spec.tertiary:
        draw.text((tx, ty + 56), spec.tertiary, fill=green, font=font_sm)


def save_overlay_png(spec: ScreenTextOverlay, path: Path) -> Path:
    from shorts_bot.config import settings

    path.parent.mkdir(parents=True, exist_ok=True)
    if settings.screen_text_screen_only and _is_phone_overlay(spec):
        render_screen_overlay_rgba(normalize_overlay_spec(spec)).save(path, "PNG")
    else:
        render_overlay_rgba(spec).save(path, "PNG")
    return path


def apply_overlay_to_video(
    video_path: Path,
    overlay_png: Path,
    dest: Path,
    *,
    spec: ScreenTextOverlay | None = None,
) -> Path:
    from shorts_bot.config import settings

    dest.parent.mkdir(parents=True, exist_ok=True)
    lay = phone_layout()
    sx, sy, sw, sh = lay.screen

    if spec is not None and _is_phone_overlay(spec) and settings.screen_text_screen_only:
        scrub = _scrub_vf_chain(spec, local=True)
        vf = (
            f"[0:v]split[base][cropin];"
            f"[cropin]crop={sw}:{sh}:{sx}:{sy},{scrub},"
            f"gblur=sigma=5,eq=brightness=-0.04:saturation=0.85[scrub];"
            f"[scrub][1:v]overlay=0:0[screen];"
            f"[base][screen]overlay={sx}:{sy}[out]"
        )
    elif spec is not None and _is_phone_overlay(spec):
        scrub = _scrub_vf_chain(spec)
        vf = (
            f"[0:v]{scrub},gblur=sigma=12,eq=brightness=-0.1:saturation=0.75[scrub];"
            f"[scrub][1:v]overlay=0:0:format=auto[out]"
        )
    else:
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


def apply_phone_scrub_only(video_path: Path, dest: Path) -> Path:
    """Blur/scrub phone display rect only — no composited UI layer."""
    lay = phone_layout()
    sx, sy, sw, sh = lay.screen
    vf = (
        f"[0:v]split[base][cropin];"
        f"[cropin]crop={sw}:{sh}:{sx}:{sy},"
        f"gblur=sigma=3,eq=brightness=-0.03:saturation=0.88[scrub];"
        f"[base][scrub]overlay={sx}:{sy}[out]"
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video_path.resolve()),
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


def _phone_segment_spoken(spoken: str) -> bool:
    lower = (spoken or "").lower()
    return any(
        k in lower
        for k in (
            "app",
            "hallway",
            "feed",
            "refresh",
            "glitch",
            "empty",
            "live alone",
            "live view",
        )
    )


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


def _trim_clip_segment(src: Path, dest: Path, *, start: float, duration: float) -> Path:
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-ss",
            f"{start:.4f}",
            "-i",
            str(src.resolve()),
            "-t",
            f"{duration:.4f}",
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


def _concat_clips(parts: list[Path], dest: Path) -> Path:
    list_file = dest.parent / f"concat_{dest.stem}.txt"
    list_file.write_text(
        "\n".join(f"file '{p.resolve()}'" for p in parts),
        encoding="utf-8",
    )
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_file),
            "-c",
            "copy",
            str(dest),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return dest


def _caption_slices_for_segment(
    segment: dict,
    captions: list[dict],
) -> list[tuple[float, float, str]]:
    seg_start = float(segment.get("start_seconds", 0))
    seg_end = float(segment.get("end_seconds", seg_start))
    slices: list[tuple[float, float, str]] = []
    for cap in captions:
        c0 = float(cap.get("start_seconds", 0))
        c1 = float(cap.get("end_seconds", c0))
        overlap_start = max(seg_start, c0)
        overlap_end = min(seg_end, c1)
        if overlap_end - overlap_start < 0.08:
            continue
        rel_start = overlap_start - seg_start
        rel_end = overlap_end - seg_start
        slices.append((rel_start, rel_end, str(cap.get("spoken_text") or "")))
    if not slices:
        return [(0.0, seg_end - seg_start, str(segment.get("spoken_text") or ""))]
    slices.sort(key=lambda x: x[0])
    return slices


def maybe_apply_screen_text(
    clip_path: Path,
    spec: ScreenTextOverlay | None,
    *,
    tmp_dir: Path,
    segment_index: int,
    segment: dict | None = None,
    captions: list[dict] | None = None,
    hook: str = "",
    topic: str = "",
) -> Path:
    from shorts_bot.production.screen_text_spec import infer_overlay_from_spoken

    out = tmp_dir / f"screen_text_{segment_index:03d}.mp4"
    if spec is None and not (segment and captions):
        apply_caption_scrub_only(clip_path, out)
        return out

    if segment and captions:
        slices = _caption_slices_for_segment(segment, captions)
        unique_specs: list[tuple[float, float, ScreenTextOverlay | None]] = []
        for rel_start, rel_end, spoken in slices:
            cap_spec = infer_overlay_from_spoken(spoken, hook=hook, topic=topic)
            ov = cap_spec if cap_spec is not None else spec
            if unique_specs and unique_specs[-1][2] == ov:
                prev_start, _, prev_ov = unique_specs[-1]
                unique_specs[-1] = (prev_start, rel_end, prev_ov)
            else:
                unique_specs.append((rel_start, rel_end, ov))

        if len(unique_specs) <= 1:
            only = unique_specs[0][2] if unique_specs else spec
            if only is None:
                spoken = str(segment.get("spoken_text") or "") if segment else ""
                if _phone_segment_spoken(spoken):
                    apply_phone_scrub_only(clip_path, out)
                else:
                    apply_caption_scrub_only(clip_path, out)
                return out
            norm = normalize_overlay_spec(only)
            from shorts_bot.config import settings

            if norm.kind in {"phone_feed", "message_bubble"} and not settings.screen_text_draw_phone_ui:
                apply_phone_scrub_only(clip_path, out)
                return out
            png = tmp_dir / f"screen_text_{segment_index:03d}.png"
            save_overlay_png(norm, png)
            apply_overlay_to_video(clip_path, png, out, spec=norm)
            return out

        parts: list[Path] = []
        for j, (rel_start, rel_end, ov) in enumerate(unique_specs):
            dur = max(0.05, rel_end - rel_start)
            sub_in = tmp_dir / f"screen_text_{segment_index:03d}_sub_{j}_in.mp4"
            sub_out = tmp_dir / f"screen_text_{segment_index:03d}_sub_{j}.mp4"
            _trim_clip_segment(clip_path, sub_in, start=rel_start, duration=dur)
            if ov is None:
                apply_caption_scrub_only(sub_in, sub_out)
            else:
                norm = normalize_overlay_spec(ov)
                from shorts_bot.config import settings

                if norm.kind in {"phone_feed", "message_bubble"} and not settings.screen_text_draw_phone_ui:
                    apply_phone_scrub_only(sub_in, sub_out)
                else:
                    png = tmp_dir / f"screen_text_{segment_index:03d}_sub_{j}.png"
                    save_overlay_png(norm, png)
                    apply_overlay_to_video(sub_in, png, sub_out, spec=norm)
            parts.append(sub_out)
        _concat_clips(parts, out)
        return out

    if spec is None:
        apply_caption_scrub_only(clip_path, out)
        return out
    norm = normalize_overlay_spec(spec)
    from shorts_bot.config import settings

    if norm.kind in {"phone_feed", "message_bubble"} and not settings.screen_text_draw_phone_ui:
        apply_phone_scrub_only(clip_path, out)
        return out
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
