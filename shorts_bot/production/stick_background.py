"""ChainsFR-style scene layers — cosy domestic sets, only what the line needs."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

# Soft Continuity cosy palette (channel/brand/cosy_aesthetic.md)
WALL_CREAM = "#F5EFE6"
FLOOR_WARM = "#E8DFD4"
LINE_INK = "#1A1A1A"
LAMP_GLOW = "#F2D98A"
SAGE = "#9DB8A0"
TERRACOTTA = "#C9A08A"


class BackgroundKind(str, Enum):
    """Scene mood — warm home first; office only when script demands it."""

    PLAIN = "plain"
    NIGHT_WINDOW = "night_window"
    MORNING_WINDOW = "morning_window"
    RAIN_WINDOW = "rain_window"
    COSY_COUCH = "cosy_couch"
    CALM_LAMP = "calm_lamp"
    TEA_KITCHEN = "tea_kitchen"
    DOOR_TENSION = "door_tension"
    PARTY_ENTRY = "party_entry"
    WORK_DESK = "work_desk"  # only when script explicitly says interview/presentation/desk


@dataclass
class RoomPlan:
    background: BackgroundKind
    wall_props: list[str]  # only these get drawn — literal to script
    foreground_prop: str | None = None
    furniture: str | None = None  # "bed" | "couch" | None — never forced every frame


def plan_room(spoken_text: str) -> RoomPlan:
    """Pick the smallest cosy set that illustrates the spoken line."""
    lower = spoken_text.lower()
    props: list[str] = []
    bg = BackgroundKind.PLAIN
    furniture: str | None = None
    fg: str | None = None

    if any(w in lower for w in ("3 am", "3am", "night", "dark", "can't sleep", "cant sleep")):
        bg = BackgroundKind.NIGHT_WINDOW
        if "lamp" in lower or "dim" in lower:
            props.append("lamp_dim")
    elif any(w in lower for w in ("tea", "mug", "warm drink", "coffee", "kitchen", "counter")):
        bg = BackgroundKind.TEA_KITCHEN
        props.append("mug")
    elif any(w in lower for w in ("sunday", "dread", "rain", "grey", "overcast", "couch", "blanket", "can't move")):
        bg = BackgroundKind.COSY_COUCH
        props.append("rain_window")
        if "blanket" in lower or "bed" not in lower:
            props.append("throw")
        furniture = "couch"
    elif any(w in lower for w in ("email", "work", "meeting", "monday")) and not any(
        w in lower for w in ("interview", "presentation", "desk", "office")
    ):
        bg = BackgroundKind.COSY_COUCH
        props.append("rain_window")
        furniture = "couch"
    elif any(w in lower for w in ("morning", "wake")) or (
        " sun" in f" {lower}" or lower.startswith("sun")
    ):
        bg = BackgroundKind.MORNING_WINDOW
    elif any(w in lower for w in ("storm",)):
        bg = BackgroundKind.RAIN_WINDOW
    elif any(w in lower for w in ("party", "crowd", "walk in", "walked in")):
        bg = BackgroundKind.PARTY_ENTRY
        props.append("door")
    elif any(w in lower for w in ("door", "conversation", "talk", "apolog", "angry", "yell")):
        bg = BackgroundKind.DOOR_TENSION
        props.append("door")
    elif any(w in lower for w in ("breathe", "breath", "calm", "still here", "ground")):
        bg = BackgroundKind.CALM_LAMP
        props.append("lamp_warm")
    elif any(w in lower for w in ("presentation", "interview", "office", "desk")):
        bg = BackgroundKind.WORK_DESK
    elif any(w in lower for w in ("sleep", "bed", "room")):
        bg = BackgroundKind.PLAIN

    if any(w in lower for w in ("bed", "sleep", "3 am", "3am", "wake", "lying", "laps")):
        furniture = "bed"
        if "blanket" in lower:
            props.append("throw")
    elif "couch" in lower or ("sit" in lower and "stand" not in lower) or bg == BackgroundKind.COSY_COUCH:
        furniture = "couch"

    if "phone" in lower or "scroll" in lower or "text" in lower:
        fg = "phone"
    elif "laptop" in lower or "email" in lower:
        fg = "laptop"
    if "clock" in lower or "3 am" in lower or "3am" in lower:
        props.append("clock")
    if "plant" in lower:
        props.append("plant")
    if "mug" in lower or "tea" in lower:
        props.append("mug")

    return RoomPlan(background=bg, wall_props=props, foreground_prop=fg, furniture=furniture)


def draw_room_background(draw, w: int, h: int, room: RoomPlan, font_reg) -> None:
    """Wall + floor; cosy lamp/window/mug only when the scene calls for it."""
    draw.rectangle([0, 0, w, int(h * 0.82)], fill=WALL_CREAM)
    draw.rectangle([0, int(h * 0.82), w, h], fill=FLOOR_WARM)
    draw.line([(0, int(h * 0.82)), (w, int(h * 0.82))], fill=LINE_INK, width=3)

    if room.background == BackgroundKind.PLAIN:
        return

    window_bgs = {
        BackgroundKind.NIGHT_WINDOW,
        BackgroundKind.MORNING_WINDOW,
        BackgroundKind.RAIN_WINDOW,
        BackgroundKind.COSY_COUCH,
        BackgroundKind.CALM_LAMP,
        BackgroundKind.TEA_KITCHEN,
    }
    if room.background in window_bgs or "rain_window" in room.wall_props:
        wx1, wy1 = int(w * 0.10), int(h * 0.14)
        wx2, wy2 = int(w * 0.45), int(h * 0.46)
        draw.rectangle([wx1, wy1, wx2, wy2], fill="#C5D8E8", outline=LINE_INK, width=3)
        inner = [wx1 + 4, wy1 + 4, wx2 - 4, wy2 - 4]
        if room.background == BackgroundKind.NIGHT_WINDOW:
            draw.rectangle(inner, fill="#2A3040")
            draw.ellipse([wx2 - 70, wy1 + 18, wx2 - 35, wy1 + 53], fill=LAMP_GLOW, outline=LINE_INK, width=2)
        elif room.background == BackgroundKind.MORNING_WINDOW:
            draw.rectangle(inner, fill="#B8D4F0")
            draw.ellipse([wx1 + 28, wy1 + 22, wx1 + 62, wy1 + 56], fill="#FFE08A", outline=LINE_INK, width=2)
        elif room.background in {BackgroundKind.RAIN_WINDOW, BackgroundKind.COSY_COUCH} or "rain_window" in room.wall_props:
            draw.rectangle(inner, fill="#A8B8C8")
            for i in range(6):
                x = wx1 + 18 + i * 38
                draw.line([(x, wy1 + 8), (x - 6, wy2 - 8)], fill="#8899AA", width=2)
        elif room.background == BackgroundKind.CALM_LAMP:
            draw.rectangle(inner, fill="#C8D0E0")
        elif room.background == BackgroundKind.TEA_KITCHEN:
            draw.rectangle(inner, fill="#D8E0E8")

    if room.background == BackgroundKind.WORK_DESK:
        _draw_side_desk(draw, int(w * 0.58), int(h * 0.52))

    if room.background in {BackgroundKind.DOOR_TENSION, BackgroundKind.PARTY_ENTRY} or "door" in room.wall_props:
        party = room.background == BackgroundKind.PARTY_ENTRY
        _draw_door(draw, int(w * 0.52), int(h * 0.12), int(h * 0.40), party=party)

    if "lamp_dim" in room.wall_props:
        _draw_floor_lamp(draw, int(w * 0.78), int(h * 0.44), dim=True)
    if "lamp_warm" in room.wall_props or room.background == BackgroundKind.CALM_LAMP:
        _draw_floor_lamp(draw, int(w * 0.76), int(h * 0.42), dim=False)
    if "plant" in room.wall_props:
        _draw_plant(draw, int(w * 0.84), int(h * 0.40))
    if "clock" in room.wall_props:
        _draw_wall_clock(draw, int(w * 0.48), int(h * 0.10))
    if "mug" in room.wall_props or room.background == BackgroundKind.TEA_KITCHEN:
        _draw_mug(draw, int(w * 0.62), int(h * 0.58))
    if "throw" in room.wall_props and room.furniture == "couch":
        _draw_throw_hint(draw, int(w * 0.20), int(h * 0.58))


def draw_couch(draw, w: int, h: int) -> tuple[int, int]:
    """Cosy couch — terracotta tones."""
    left, top = int(w * 0.18), int(h * 0.60)
    right, seat_y = int(w * 0.82), int(h * 0.70)
    back_h = int(h * 0.06)
    base_bot = seat_y + int(h * 0.04)
    draw.rounded_rectangle(
        [left, top, right, base_bot],
        radius=16,
        fill=TERRACOTTA,
        outline=LINE_INK,
        width=3,
    )
    draw.rounded_rectangle(
        [left, top, right, top + back_h],
        radius=12,
        fill="#B89078",
        outline=LINE_INK,
        width=2,
    )
    cx = (left + right) // 2
    return cx, seat_y - 18


def draw_bed(draw, w: int, h: int) -> tuple[int, int]:
    """Simple bed — warm linen tones."""
    left, top = int(w * 0.14), int(h * 0.64)
    right, bot = int(w * 0.86), int(h * 0.72)
    draw.rectangle([left, top, right, bot], fill="#E0D6CC", outline=LINE_INK, width=3)
    draw.rectangle([left, top - 28, right, top], fill="#F0E8E0", outline=LINE_INK, width=2)
    cx = (left + right) // 2
    return cx, top - 10


def _draw_floor_lamp(draw, x: int, y: int, *, dim: bool) -> None:
    color = LAMP_GLOW if not dim else "#C4A870"
    draw.line([(x, y + 70), (x, y + 180)], fill=LINE_INK, width=3)
    draw.polygon([(x - 30, y), (x + 30, y), (x + 18, y + 42), (x - 18, y + 42)], fill=color, outline=LINE_INK, width=2)


def _draw_plant(draw, x: int, y: int) -> None:
    draw.rectangle([x - 12, y + 35, x + 12, y + 80], fill="#8B7355", outline=LINE_INK, width=2)
    draw.ellipse([x - 28, y, x + 28, y + 48], fill=SAGE, outline=LINE_INK, width=2)


def _draw_mug(draw, x: int, y: int) -> None:
    draw.rounded_rectangle([x, y, x + 44, y + 36], radius=6, fill="#F8F4EE", outline=LINE_INK, width=2)
    draw.arc([x + 38, y + 8, x + 56, y + 28], start=270, end=90, fill=LINE_INK, width=2)
    draw.ellipse([x + 6, y + 4, x + 38, y + 14], fill="#D4C4A8", outline=LINE_INK, width=1)


def _draw_throw_hint(draw, x: int, y: int) -> None:
    draw.rounded_rectangle([x, y, x + 100, y + 50], radius=10, fill=SAGE, outline=LINE_INK, width=2)


def _draw_wall_clock(draw, x: int, y: int) -> None:
    draw.ellipse([x - 30, y, x + 30, y + 60], outline=LINE_INK, width=2, fill="#FFFFFF")
    draw.line([(x, y + 30), (x, y + 14)], fill=LINE_INK, width=2)
    draw.line([(x, y + 30), (x + 16, y + 30)], fill=LINE_INK, width=2)


def _draw_door(draw, x: int, y: int, height: int, *, party: bool = False) -> None:
    fill = "#8A7060" if party else "#A89080"
    draw.rectangle([x, y, x + 90, y + height], fill=fill, outline=LINE_INK, width=3)
    draw.ellipse([x + 70, y + height // 2, x + 82, y + height // 2 + 10], fill="#D4A830", outline=LINE_INK, width=2)


def _draw_side_desk(draw, x: int, y: int) -> None:
    draw.rectangle([x, y, x + 120, y + 10], fill="#9A8A78", outline=LINE_INK, width=2)
    draw.rectangle([x + 16, y - 42, x + 88, y], fill="#E0E0E0", outline=LINE_INK, width=2)


def draw_foreground_prop(draw, cx: int, cy: int, prop: str | None) -> None:
    if prop == "laptop":
        lx = cx + 140
        draw.rectangle([lx, cy - 24, lx + 80, cy + 8], fill="#888888", outline=LINE_INK, width=2)
        draw.rectangle([lx + 4, cy - 48, lx + 76, cy - 22], fill="#C0C0C0", outline=LINE_INK, width=2)
    elif prop == "phone":
        px = cx + 120
        draw.rounded_rectangle([px, cy - 16, px + 36, cy + 44], radius=5, outline=LINE_INK, width=2, fill="#222222")
