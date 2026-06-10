"""ChainsFR-style scene layers — minimal MS-Paint sets, only what the line needs."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class BackgroundKind(str, Enum):
    """Scene mood — not every frame needs a full room."""

    PLAIN = "plain"
    NIGHT_WINDOW = "night_window"
    MORNING_WINDOW = "morning_window"
    RAIN_WINDOW = "rain_window"
    SUNDAY_GREY = "sunday_grey"
    WORK_DESK = "work_desk"
    DOOR_TENSION = "door_tension"
    PARTY_ENTRY = "party_entry"
    CALM_LAMP = "calm_lamp"


@dataclass
class RoomPlan:
    background: BackgroundKind
    wall_props: list[str]  # only these get drawn — literal to script
    foreground_prop: str | None = None
    furniture: str | None = None  # "bed" | "couch" | None — never forced every frame


def plan_room(spoken_text: str) -> RoomPlan:
    """Pick the smallest set that illustrates the spoken line (ChainsFR minimalism)."""
    lower = spoken_text.lower()
    props: list[str] = []
    bg = BackgroundKind.PLAIN
    furniture: str | None = None
    fg: str | None = None

    if any(w in lower for w in ("3 am", "3am", "night", "dark", "can't sleep", "cant sleep")):
        bg = BackgroundKind.NIGHT_WINDOW
        if "lamp" in lower or "dim" in lower:
            props.append("lamp_dim")
    elif any(w in lower for w in ("sunday", "dread", "monday", "email", "work", "meeting")):
        bg = BackgroundKind.SUNDAY_GREY
        if "calendar" in lower or "sunday" in lower or "monday" in lower:
            props.append("calendar")
    elif any(w in lower for w in ("morning", "wake")) or (
        " sun" in f" {lower}" or lower.startswith("sun")
    ):
        bg = BackgroundKind.MORNING_WINDOW
    elif any(w in lower for w in ("rain", "storm", "grey sky")):
        bg = BackgroundKind.RAIN_WINDOW
    elif any(w in lower for w in ("party", "crowd", "walk in", "walked in")):
        bg = BackgroundKind.PARTY_ENTRY
        props.append("door")
    elif any(w in lower for w in ("door", "conversation", "talk", "apolog", "angry", "yell")):
        bg = BackgroundKind.DOOR_TENSION
        props.append("door")
    elif any(w in lower for w in ("breathe", "breath", "calm", "still here")):
        bg = BackgroundKind.CALM_LAMP
        if "lamp" in lower or "calm" in lower:
            props.append("lamp_warm")
    elif any(w in lower for w in ("presentation", "interview", "doctor", "desk")):
        bg = BackgroundKind.WORK_DESK
    elif any(w in lower for w in ("sleep", "bed", "room")):
        bg = BackgroundKind.PLAIN

    if any(w in lower for w in ("bed", "sleep", "3 am", "3am", "wake", "lying", "laps")):
        furniture = "bed"
    elif "couch" in lower or ("sit" in lower and "stand" not in lower):
        furniture = "couch"

    if "phone" in lower or "scroll" in lower or "text" in lower:
        fg = "phone"
    elif "laptop" in lower or "email" in lower:
        fg = "laptop"
    if "clock" in lower or "3 am" in lower or "3am" in lower:
        props.append("clock")
    if "plant" in lower:
        props.append("plant")

    return RoomPlan(background=bg, wall_props=props, foreground_prop=fg, furniture=furniture)


def draw_room_background(draw, w: int, h: int, room: RoomPlan, font_reg) -> None:
    """Wall + floor; add window/door/lamp only when the scene calls for it."""
    wall = "#F4F4F0"
    draw.rectangle([0, 0, w, int(h * 0.82)], fill=wall)
    draw.rectangle([0, int(h * 0.82), w, h], fill="#E8E5DE")
    draw.line([(0, int(h * 0.82)), (w, int(h * 0.82))], fill="#111111", width=3)

    if room.background == BackgroundKind.PLAIN:
        return

    if room.background in {
        BackgroundKind.NIGHT_WINDOW,
        BackgroundKind.MORNING_WINDOW,
        BackgroundKind.RAIN_WINDOW,
        BackgroundKind.SUNDAY_GREY,
        BackgroundKind.CALM_LAMP,
    }:
        wx1, wy1 = int(w * 0.10), int(h * 0.14)
        wx2, wy2 = int(w * 0.45), int(h * 0.46)
        draw.rectangle([wx1, wy1, wx2, wy2], fill="#C5D8E8", outline="#111111", width=3)
        inner = [wx1 + 4, wy1 + 4, wx2 - 4, wy2 - 4]
        if room.background == BackgroundKind.NIGHT_WINDOW:
            draw.rectangle(inner, fill="#1A2030")
            draw.ellipse([wx2 - 70, wy1 + 18, wx2 - 35, wy1 + 53], fill="#F0E6B0", outline="#111111", width=2)
        elif room.background == BackgroundKind.MORNING_WINDOW:
            draw.rectangle(inner, fill="#B8D4F0")
            draw.ellipse([wx1 + 28, wy1 + 22, wx1 + 62, wy1 + 56], fill="#FFE08A", outline="#111111", width=2)
        elif room.background == BackgroundKind.RAIN_WINDOW:
            draw.rectangle(inner, fill="#8A9AAA")
            for i in range(6):
                x = wx1 + 18 + i * 38
                draw.line([(x, wy1 + 8), (x - 6, wy2 - 8)], fill="#667788", width=2)
        elif room.background == BackgroundKind.SUNDAY_GREY:
            draw.rectangle(inner, fill="#9AA0A8")
        elif room.background == BackgroundKind.CALM_LAMP:
            draw.rectangle(inner, fill="#C8D0E0")

    if room.background == BackgroundKind.WORK_DESK:
        _draw_side_desk(draw, int(w * 0.58), int(h * 0.52))

    if room.background in {BackgroundKind.DOOR_TENSION, BackgroundKind.PARTY_ENTRY} or "door" in room.wall_props:
        party = room.background == BackgroundKind.PARTY_ENTRY
        _draw_door(draw, int(w * 0.52), int(h * 0.12), int(h * 0.40), party=party)

    if "lamp_dim" in room.wall_props:
        _draw_floor_lamp(draw, int(w * 0.78), int(h * 0.44), dim=True)
    if "lamp_warm" in room.wall_props or room.background == BackgroundKind.CALM_LAMP:
        _draw_floor_lamp(draw, int(w * 0.76), int(h * 0.42), dim=False)
    if "calendar" in room.wall_props:
        _draw_wall_calendar(draw, int(w * 0.54), int(h * 0.16), font_reg)
    if "plant" in room.wall_props:
        _draw_plant(draw, int(w * 0.84), int(h * 0.40))
    if "clock" in room.wall_props:
        _draw_wall_clock(draw, int(w * 0.48), int(h * 0.10))


def draw_couch(draw, w: int, h: int) -> tuple[int, int]:
    """Optional couch — only when script mentions sitting/couch."""
    left, top = int(w * 0.18), int(h * 0.60)
    right, seat_y = int(w * 0.82), int(h * 0.70)
    back_h = int(h * 0.06)
    base_bot = seat_y + int(h * 0.04)
    draw.rounded_rectangle(
        [left, top, right, base_bot],
        radius=16,
        fill="#C4B8A8",
        outline="#111111",
        width=3,
    )
    draw.rounded_rectangle(
        [left, top, right, top + back_h],
        radius=12,
        fill="#B8A898",
        outline="#111111",
        width=2,
    )
    cx = (left + right) // 2
    return cx, seat_y - 18


def draw_bed(draw, w: int, h: int) -> tuple[int, int]:
    """Simple bed line — ChainsFR sleep beats, not a locked couch set."""
    left, top = int(w * 0.14), int(h * 0.64)
    right, bot = int(w * 0.86), int(h * 0.72)
    draw.rectangle([left, top, right, bot], fill="#D8D0C8", outline="#111111", width=3)
    draw.rectangle([left, top - 28, right, top], fill="#E8E0D8", outline="#111111", width=2)
    cx = (left + right) // 2
    return cx, top - 10


def _draw_floor_lamp(draw, x: int, y: int, *, dim: bool) -> None:
    color = "#E8D8A0" if not dim else "#A09070"
    draw.line([(x, y + 70), (x, y + 180)], fill="#111111", width=3)
    draw.polygon([(x - 30, y), (x + 30, y), (x + 18, y + 42), (x - 18, y + 42)], fill=color, outline="#111111", width=2)


def _draw_plant(draw, x: int, y: int) -> None:
    draw.rectangle([x - 12, y + 35, x + 12, y + 80], fill="#8B7355", outline="#111111", width=2)
    draw.ellipse([x - 28, y, x + 28, y + 48], fill="#6A9A5B", outline="#111111", width=2)


def _draw_wall_clock(draw, x: int, y: int) -> None:
    draw.ellipse([x - 30, y, x + 30, y + 60], outline="#111111", width=2, fill="#FFFFFF")
    draw.line([(x, y + 30), (x, y + 14)], fill="#111111", width=2)
    draw.line([(x, y + 30), (x + 16, y + 30)], fill="#111111", width=2)


def _draw_wall_calendar(draw, x: int, y: int, font) -> None:
    draw.rectangle([x, y, x + 80, y + 60], fill="#FFFFFF", outline="#111111", width=2)
    draw.rectangle([x, y, x + 80, y + 18], fill="#CC4444", outline="#111111", width=2)
    draw.text((x + 6, y + 24), "SUN", fill="#111111", font=font)


def _draw_door(draw, x: int, y: int, height: int, *, party: bool = False) -> None:
    fill = "#6A5040" if party else "#A09080"
    draw.rectangle([x, y, x + 90, y + height], fill=fill, outline="#111111", width=3)
    draw.ellipse([x + 70, y + height // 2, x + 82, y + height // 2 + 10], fill="#D4A830", outline="#111111", width=2)


def _draw_side_desk(draw, x: int, y: int) -> None:
    draw.rectangle([x, y, x + 120, y + 10], fill="#9A8A78", outline="#111111", width=2)
    draw.rectangle([x + 16, y - 42, x + 88, y], fill="#E0E0E0", outline="#111111", width=2)


def draw_foreground_prop(draw, cx: int, cy: int, prop: str | None) -> None:
    if prop == "laptop":
        lx = cx + 140
        draw.rectangle([lx, cy - 24, lx + 80, cy + 8], fill="#888888", outline="#111111", width=2)
        draw.rectangle([lx + 4, cy - 48, lx + 76, cy - 22], fill="#C0C0C0", outline="#111111", width=2)
    elif prop == "phone":
        px = cx + 120
        draw.rounded_rectangle([px, cy - 16, px + 36, cy + 44], radius=5, outline="#111111", width=2, fill="#222222")
