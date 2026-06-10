"""ChainsFR-style stick figure frames — minimal sets, expressive poses."""

from __future__ import annotations

import textwrap
from pathlib import Path

from shorts_bot.production.image_prompts import ImageBrief
from shorts_bot.production.scene_plan import Pose, plan_scene
from shorts_bot.production.stick_background import (
    draw_bed,
    draw_couch,
    draw_foreground_prop,
    draw_room_background,
    plan_room,
)


def _font(size: int):
    from PIL import ImageFont

    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except OSError:
        return ImageFont.load_default()


def _font_reg(size: int):
    from PIL import ImageFont

    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()


def _draw_stick(draw, cx: int, cy: int, pose: Pose, scale: float = 1.0) -> None:
    s = scale
    head_r = int(28 * s)
    body_top = cy
    body_bot = cy + int(120 * s)
    draw.ellipse([cx - head_r, body_top - head_r * 2, cx + head_r, body_top], fill="#111111", outline="#111111")

    if pose == Pose.LYING_AWAKE:
        hx, hy = cx - int(20 * s), cy + int(10 * s)
        draw.ellipse([hx - head_r, hy - head_r, hx + head_r, hy + head_r], fill="#111111")
        draw.line([hx + int(10 * s), hy, hx + int(70 * s), hy + int(15 * s)], fill="#111111", width=int(5 * s))
        draw.line([hx + int(40 * s), hy + int(10 * s), hx + int(20 * s), hy + int(50 * s)], fill="#111111", width=int(4 * s))
        draw.line([hx + int(40 * s), hy + int(10 * s), hx + int(65 * s), hy + int(45 * s)], fill="#111111", width=int(4 * s))
        return

    if pose == Pose.CALM_IN_BED:
        hx, hy = cx, cy + int(20 * s)
        draw.ellipse([hx - head_r, hy - head_r, hx + head_r, hy + head_r], fill="#111111")
        draw.line([hx, hy + head_r, hx, hy + int(55 * s)], fill="#111111", width=int(5 * s))
        draw.line([hx, hy + int(25 * s), hx - int(40 * s), hy + int(45 * s)], fill="#111111", width=int(4 * s))
        draw.line([hx, hy + int(25 * s), hx + int(40 * s), hy + int(45 * s)], fill="#111111", width=int(4 * s))
        return

    draw.line([cx, body_top, cx, body_bot], fill="#111111", width=int(6 * s))

    if pose == Pose.BREATHING:
        draw.line([cx, body_top + int(20 * s), cx - int(55 * s), body_top + int(70 * s)], fill="#111111", width=int(5 * s))
        draw.line([cx, body_top + int(20 * s), cx + int(55 * s), body_top + int(70 * s)], fill="#111111", width=int(5 * s))
        draw.line([cx, body_bot, cx - int(35 * s), body_bot + int(55 * s)], fill="#111111", width=int(5 * s))
        draw.line([cx, body_bot, cx + int(35 * s), body_bot + int(55 * s)], fill="#111111", width=int(5 * s))
        for i, dx in enumerate((-90, -60, -30)):
            draw.arc([cx + dx - 20, body_top - 50 - i * 15, cx + dx + 20, body_top - 10 - i * 15], 200, 340, fill="#888888", width=2)
    elif pose == Pose.REACHING_PHONE:
        draw.line([cx, body_top + int(25 * s), cx - int(40 * s), body_top + int(75 * s)], fill="#111111", width=int(5 * s))
        draw.line([cx, body_top + int(25 * s), cx + int(70 * s), body_top + int(50 * s)], fill="#111111", width=int(5 * s))
        draw.line([cx, body_bot, cx - int(30 * s), body_bot + int(60 * s)], fill="#111111", width=int(5 * s))
        draw.line([cx, body_bot, cx + int(30 * s), body_bot + int(60 * s)], fill="#111111", width=int(5 * s))
    elif pose == Pose.PUTTING_PHONE_DOWN:
        draw.line([cx, body_top + int(25 * s), cx - int(65 * s), body_top + int(55 * s)], fill="#111111", width=int(5 * s))
        draw.line([cx, body_top + int(20 * s), cx + int(40 * s), body_top + int(80 * s)], fill="#111111", width=int(5 * s))
        draw.line([cx, body_bot, cx - int(35 * s), body_bot + int(55 * s)], fill="#111111", width=int(5 * s))
        draw.line([cx, body_bot, cx + int(35 * s), body_bot + int(55 * s)], fill="#111111", width=int(5 * s))
    elif pose == Pose.NAMING_THOUGHT:
        draw.line([cx, body_top + int(20 * s), cx - int(50 * s), body_top + int(15 * s)], fill="#111111", width=int(5 * s))
        draw.line([cx, body_top + int(20 * s), cx + int(50 * s), body_top + int(60 * s)], fill="#111111", width=int(5 * s))
        draw.line([cx, body_bot, cx - int(32 * s), body_bot + int(58 * s)], fill="#111111", width=int(5 * s))
        draw.line([cx, body_bot, cx + int(32 * s), body_bot + int(58 * s)], fill="#111111", width=int(5 * s))
    elif pose == Pose.HUDDLED:
        draw.line([cx, body_top + int(15 * s), cx - int(45 * s), body_top + int(55 * s)], fill="#111111", width=int(5 * s))
        draw.line([cx, body_top + int(15 * s), cx + int(45 * s), body_top + int(55 * s)], fill="#111111", width=int(5 * s))
        draw.line([cx, body_bot, cx - int(25 * s), body_bot + int(45 * s)], fill="#111111", width=int(5 * s))
        draw.line([cx, body_bot, cx + int(25 * s), body_bot + int(45 * s)], fill="#111111", width=int(5 * s))
    elif pose == Pose.WALKING:
        draw.line([cx, body_top + int(20 * s), cx - int(55 * s), body_top + int(45 * s)], fill="#111111", width=int(5 * s))
        draw.line([cx, body_top + int(25 * s), cx + int(50 * s), body_top + int(35 * s)], fill="#111111", width=int(5 * s))
        draw.line([cx, body_bot, cx - int(20 * s), body_bot + int(65 * s)], fill="#111111", width=int(5 * s))
        draw.line([cx, body_bot, cx + int(45 * s), body_bot + int(50 * s)], fill="#111111", width=int(5 * s))
    elif pose == Pose.POINTING_SELF:
        draw.line([cx, body_top + int(20 * s), cx - int(45 * s), body_top + int(70 * s)], fill="#111111", width=int(5 * s))
        draw.line([cx, body_top + int(20 * s), cx + int(55 * s), body_top + int(35 * s)], fill="#111111", width=int(5 * s))
        draw.line([cx, body_bot, cx - int(30 * s), body_bot + int(58 * s)], fill="#111111", width=int(5 * s))
        draw.line([cx, body_bot, cx + int(30 * s), body_bot + int(58 * s)], fill="#111111", width=int(5 * s))
    else:
        draw.line([cx, body_top + int(20 * s), cx - int(45 * s), body_top + int(70 * s)], fill="#111111", width=int(5 * s))
        draw.line([cx, body_top + int(20 * s), cx + int(45 * s), body_top + int(70 * s)], fill="#111111", width=int(5 * s))
        draw.line([cx, body_bot, cx - int(32 * s), body_bot + int(58 * s)], fill="#111111", width=int(5 * s))
        draw.line([cx, body_bot, cx + int(32 * s), body_bot + int(58 * s)], fill="#111111", width=int(5 * s))


def _draw_prop(draw, cx: int, cy: int, prop: str | None, pose: Pose) -> None:
    if prop == "phone":
        px = cx + 120 if pose == Pose.REACHING_PHONE else cx - 140
        py = cy + 80
        draw.rounded_rectangle([px, py, px + 50, py + 90], radius=8, outline="#111111", width=4, fill="#E8E8E8")
        draw.line([px + 10, py + 70, px + 40, py + 70], fill="#111111", width=2)
    elif prop == "clock":
        draw.ellipse([cx + 180, cy - 180, cx + 280, cy - 80], outline="#111111", width=4, fill="#FFFFFF")
        draw.line([cx + 230, cy - 130, cx + 230, cy - 110], fill="#111111", width=3)
        draw.line([cx + 230, cy - 130, cx + 250, cy - 125], fill="#111111", width=3)
        draw.text((cx + 215, cy - 75), "3AM", fill="#111111", font=_font_reg(18))
    elif prop == "thought":
        tx, ty = cx + 100, cy - 200
        draw.ellipse([tx, ty, tx + 30, ty + 30], fill="#FFFFFF", outline="#111111", width=2)
        draw.ellipse([tx + 25, ty + 20, tx + 50, ty + 50], fill="#FFFFFF", outline="#111111", width=2)


def _draw_bubble(draw, text: str, w: int, h: int) -> None:
    font = _font_reg(32)
    lines = textwrap.wrap(text, width=22)
    line_h = 38
    pad = 24
    bw = min(w - 80, max(280, max(len(ln) for ln in lines) * 18 + pad * 2))
    bh = len(lines) * line_h + pad * 2
    bx = (w - bw) // 2
    by = int(h * 0.08)
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=20, fill="#FFFFFF", outline="#111111", width=4)
    tail_cx = bx + bw // 2
    draw.polygon([(tail_cx - 15, by + bh), (tail_cx + 15, by + bh), (tail_cx, by + bh + 25)], fill="#FFFFFF", outline="#111111")
    draw.line([tail_cx - 14, by + bh, tail_cx + 14, by + bh], fill="#FFFFFF", width=3)
    y = by + pad
    for ln in lines:
        draw.text((bx + pad, y), ln, fill="#111111", font=font)
        y += line_h


def _place_figure(w: int, h: int, plan, room, *, x_offset: int = 0) -> tuple[int, int, float]:
    """Anchor figure in upper safe action zone — clear of captions + right UI rail."""
    from shorts_bot.production.framing import action_figure_position

    base_x, base_y = action_figure_position(width=w, height=h)
    base_x += x_offset
    if room.furniture == "couch":
        return base_x, int(h * 0.48), 0.95
    if room.furniture == "bed" or plan.pose in {Pose.LYING_AWAKE, Pose.CALM_IN_BED}:
        return base_x - 20, int(h * 0.44), 0.9
    if plan.pose in {Pose.STANDING_CALM, Pose.POINTING_SELF}:
        return base_x, int(h * 0.38), 1.0
    return base_x, base_y, 1.0


def render_stick_frame(
    brief: ImageBrief,
    out_path: Path,
    *,
    beat_hint: str | None = None,
    figure_x_offset: int = 0,
) -> bool:
    from PIL import Image, ImageDraw

    plan = plan_scene(brief.spoken_text, beat_hint=beat_hint)
    room = plan_room(brief.spoken_text)
    w, h = 1080, 1920
    img = Image.new("RGB", (w, h), "#F4F4F0")
    draw = ImageDraw.Draw(img)

    draw_room_background(draw, w, h, room, _font_reg(16))

    fig_x, fig_y, scale = _place_figure(w, h, plan, room, x_offset=figure_x_offset)
    if room.furniture == "couch":
        fig_x, seat_y = draw_couch(draw, w, h)
        fig_y = seat_y - 90
        if plan.pose in {Pose.LYING_AWAKE, Pose.CALM_IN_BED}:
            fig_x, fig_y = fig_x - 30, seat_y - 20
    elif room.furniture == "bed" or plan.pose in {Pose.LYING_AWAKE, Pose.CALM_IN_BED}:
        fig_x, bed_top = draw_bed(draw, w, h)
        fig_y = bed_top - 8

    _draw_stick(draw, fig_x, fig_y, plan.pose, scale=scale)

    prop = plan.prop or room.foreground_prop
    if prop:
        _draw_prop(draw, fig_x, fig_y, prop, plan.pose)
        if room.foreground_prop and room.foreground_prop != plan.prop:
            draw_foreground_prop(draw, fig_x, fig_y, room.foreground_prop)

    if plan.bubble_text:
        _draw_bubble(draw, plan.bubble_text, w, h)

    from shorts_bot.production.captions import burn_captions_on_frames
    from shorts_bot.production.caption_overlay import draw_bottom_caption

    if burn_captions_on_frames():
        draw_bottom_caption(draw, brief.spoken_text, w, h)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG")
    return True


def render_all_stickfigures(
    briefs: list[ImageBrief],
    images_dir: Path,
    *,
    visual_beats: list[str] | None = None,
    figure_x_offset: int = 0,
) -> int:
    count = 0
    beats = visual_beats or []
    for i, b in enumerate(briefs):
        hint = beats[i % len(beats)] if beats else None
        path = images_dir / f"{b.filename_stem}.png"
        if render_stick_frame(b, path, beat_hint=hint, figure_x_offset=figure_x_offset):
            count += 1
    return count
