"""ChainsFR-style stick figure frames with speech bubbles."""

from __future__ import annotations

import textwrap
from pathlib import Path

from shorts_bot.production.image_prompts import ImageBrief
from shorts_bot.production.scene_plan import Pose, ScenePlan, plan_scene


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
        # Horizontal on bed level
        hx, hy = cx - int(80 * s), cy + int(40 * s)
        draw.ellipse([hx - head_r, hy - head_r, hx + head_r, hy + head_r], fill="#111111")
        draw.line([hx + head_r, hy, hx + int(100 * s), hy], fill="#111111", width=int(5 * s))
        draw.line([hx + int(50 * s), hy, hx + int(30 * s), hy - int(40 * s)], fill="#111111", width=int(4 * s))
        draw.line([hx + int(50 * s), hy, hx + int(70 * s), hy + int(25 * s)], fill="#111111", width=int(4 * s))
        return

    if pose == Pose.CALM_IN_BED:
        hx, hy = cx, cy + int(60 * s)
        draw.ellipse([hx - head_r, hy - head_r, hx + head_r, hy + head_r], fill="#111111")
        draw.line([hx, hy + head_r, hx, hy + int(90 * s)], fill="#111111", width=int(5 * s))
        draw.line([hx, hy + int(40 * s), hx - int(45 * s), hy + int(20 * s)], fill="#111111", width=int(4 * s))
        draw.line([hx, hy + int(40 * s), hx + int(45 * s), hy + int(20 * s)], fill="#111111", width=int(4 * s))
        return

    # Standing poses — shared body
    draw.line([cx, body_top, cx, body_bot], fill="#111111", width=int(6 * s))

    if pose == Pose.BREATHING:
        draw.line([cx, body_top + int(20 * s), cx - int(55 * s), body_top + int(70 * s)], fill="#111111", width=int(5 * s))
        draw.line([cx, body_top + int(20 * s), cx + int(55 * s), body_top + int(70 * s)], fill="#111111", width=int(5 * s))
        draw.line([cx, body_bot, cx - int(35 * s), body_bot + int(55 * s)], fill="#111111", width=int(5 * s))
        draw.line([cx, body_bot, cx + int(35 * s), body_bot + int(55 * s)], fill="#111111", width=int(5 * s))
        # breath lines
        for i, dx in enumerate((-90, -60, -30)):
            draw.arc([cx + dx - 20, body_top - 50 - i * 15, cx + dx + 20, body_top - 10 - i * 15], 200, 340, fill="#888888", width=2)
    elif pose == Pose.REACHING_PHONE:
        draw.line([cx, body_top + int(25 * s), cx - int(40 * s), body_top + int(75 * s)], fill="#111111", width=int(5 * s))
        draw.line([cx, body_top + int(25 * s), cx + int(70 * s), body_top + int(50 * s)], fill="#111111", width=int(5 * s))
        draw.line([cx, body_bot, cx - int(30 * s), body_bot + int(60 * s)], fill="#111111", width=int(5 * s))
        draw.line([cx, body_bot, cx + int(30 * s), body_bot + int(60 * s)], fill="#111111", width=int(5 * s))
    elif pose == Pose.PUTTING_PHONE_DOWN:
        draw.line([cx, body_top + int(25 * s), cx - int(65 * s), body_top + int(55 * s)], fill="#111111", width=int(5 * s))
        draw.line([cx, body_top + int(25 * s), cx + int(40 * s), body_top + int(80 * s)], fill="#111111", width=int(5 * s))
        draw.line([cx, body_bot, cx - int(35 * s), body_bot + int(55 * s)], fill="#111111", width=int(5 * s))
        draw.line([cx, body_bot, cx + int(35 * s), body_bot + int(55 * s)], fill="#111111", width=int(5 * s))
    elif pose == Pose.NAMING_THOUGHT:
        draw.line([cx, body_top + int(20 * s), cx - int(50 * s), body_top + int(15 * s)], fill="#111111", width=int(5 * s))
        draw.line([cx, body_top + int(20 * s), cx + int(50 * s), body_top + int(60 * s)], fill="#111111", width=int(5 * s))
        draw.line([cx, body_bot, cx - int(32 * s), body_bot + int(58 * s)], fill="#111111", width=int(5 * s))
        draw.line([cx, body_bot, cx + int(32 * s), body_bot + int(58 * s)], fill="#111111", width=int(5 * s))
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


def _draw_bottom_caption(draw, text: str, w: int, h: int) -> None:
    font = _font_reg(36)
    lines = textwrap.wrap(" ".join(text.split()), width=28)[:2]
    if not lines:
        return
    line_h = 44
    pad = 20
    bar_h = len(lines) * line_h + pad * 2
    by = h - bar_h - 80
    draw.rounded_rectangle([40, by, w - 40, by + bar_h], radius=14, fill="#111111", outline="#111111")
    y = by + pad
    for ln in lines:
        tw = draw.textlength(ln, font=font) if hasattr(draw, "textlength") else len(ln) * 18
        draw.text(((w - tw) / 2, y), ln, fill="#FFFFFF", font=font)
        y += line_h


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
    # tail
    tail_cx = bx + bw // 2
    draw.polygon([(tail_cx - 15, by + bh), (tail_cx + 15, by + bh), (tail_cx, by + bh + 25)], fill="#FFFFFF", outline="#111111")
    draw.line([tail_cx - 14, by + bh, tail_cx + 14, by + bh], fill="#FFFFFF", width=3)
    y = by + pad
    for ln in lines:
        draw.text((bx + pad, y), ln, fill="#111111", font=font)
        y += line_h


def _draw_bed_floor(draw, w: int, h: int, pose: Pose) -> None:
    floor_y = int(h * 0.78)
    if pose in {Pose.LYING_AWAKE, Pose.CALM_IN_BED}:
        draw.rounded_rectangle([80, floor_y - 40, w - 80, floor_y + 30], radius=12, fill="#E0DDD6", outline="#BBBBBB", width=2)
        draw.line([(100, floor_y - 10), (w - 100, floor_y - 10)], fill="#C8C5BE", width=2)
    else:
        draw.line([(60, floor_y), (w - 60, floor_y)], fill="#CCCCCC", width=3)


def render_stick_frame(brief: ImageBrief, out_path: Path) -> bool:
    from PIL import Image, ImageDraw

    plan = plan_scene(brief.spoken_text)
    w, h = 1080, 1920
    img = Image.new("RGB", (w, h), "#F4F4F0")
    draw = ImageDraw.Draw(img)

    _draw_bed_floor(draw, w, h, plan.pose)
    cx, cy = w // 2, int(h * 0.52)
    _draw_stick(draw, cx, cy, plan.pose)
    _draw_prop(draw, cx, cy, plan.prop, plan.pose)

    if plan.bubble_text:
        _draw_bubble(draw, plan.bubble_text, w, h)

    # Bottom subtitle — Jenny mute-safe + always-on captions
    _draw_bottom_caption(draw, brief.spoken_text, w, h)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG")
    return True


def render_all_stickfigures(briefs: list[ImageBrief], images_dir: Path) -> int:
    count = 0
    for b in briefs:
        path = images_dir / f"{b.filename_stem}.png"
        if render_stick_frame(b, path):
            count += 1
    return count
