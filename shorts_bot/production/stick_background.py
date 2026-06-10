"""ChainsFR-style room layers — fixed couch, rotating background props."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class BackgroundKind(str, Enum):
    """Background mood behind the same couch."""

    DEFAULT_ROOM = "default_room"
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
    wall_props: list[str]  # plant, clock, shelf, calendar, etc.
    foreground_prop: str | None = None


def plan_room(spoken_text: str) -> RoomPlan:
    lower = spoken_text.lower()
    props: list[str] = []

    if any(w in lower for w in ("3 am", "3am", "dark", "night", "sleep", "bed")):
        bg = BackgroundKind.NIGHT_WINDOW
        props = ["moon", "lamp_dim"]
    elif any(w in lower for w in ("sunday", "dread", "monday", "email", "work", "meeting")):
        bg = BackgroundKind.SUNDAY_GREY
        props = ["calendar", "laptop_glow"]
    elif any(w in lower for w in ("rain", "storm", "grey sky")):
        bg = BackgroundKind.RAIN_WINDOW
        props = ["rain", "plant"]
    elif any(w in lower for w in ("party", "crowd", "alone", "walk in")):
        bg = BackgroundKind.PARTY_ENTRY
        props = ["door", "coat_hook"]
    elif any(w in lower for w in ("conversation", "talk", "apolog", "text", "reply", "angry")):
        bg = BackgroundKind.DOOR_TENSION
        props = ["door", "phone_table"]
    elif any(w in lower for w in ("breathe", "breath", "calm", "still here", "good.")):
        bg = BackgroundKind.CALM_LAMP
        props = ["lamp_warm", "plant"]
    elif any(w in lower for w in ("morning", "wake", "sun")):
        bg = BackgroundKind.MORNING_WINDOW
        props = ["sun", "plant"]
    elif any(w in lower for w in ("phone", "scroll", "doom")):
        bg = BackgroundKind.NIGHT_WINDOW
        props = ["phone_glow", "lamp_dim"]
    elif any(w in lower for w in ("presentation", "interview", "doctor")):
        bg = BackgroundKind.WORK_DESK
        props = ["clock", "papers"]
    else:
        bg = BackgroundKind.DEFAULT_ROOM
        props = ["plant", "clock"]

    fg = None
    if "phone" in lower:
        fg = "phone"
    elif "laptop" in lower or "email" in lower:
        fg = "laptop"

    return RoomPlan(background=bg, wall_props=props, foreground_prop=fg)


# Couch anchor — same geometry every frame (ChainsFR room continuity)
COUCH_LEFT_RATIO = 0.12
COUCH_RIGHT_RATIO = 0.88
COUCH_TOP_RATIO = 0.58
COUCH_SEAT_Y_RATIO = 0.68


def couch_bounds(w: int, h: int) -> tuple[int, int, int, int]:
    left = int(w * COUCH_LEFT_RATIO)
    right = int(w * COUCH_RIGHT_RATIO)
    top = int(h * COUCH_TOP_RATIO)
    seat = int(h * COUCH_SEAT_Y_RATIO)
    return left, top, right, seat


def draw_room_background(draw, w: int, h: int, room: RoomPlan, font_reg) -> None:
    """Wall + window + props (behind couch)."""
    wall = "#E8E5DE"
    draw.rectangle([0, 0, w, int(h * 0.78)], fill=wall)
    draw.rectangle([0, int(h * 0.78), w, h], fill="#D8D4CC")

    wx1, wy1 = int(w * 0.08), int(h * 0.12)
    wx2, wy2 = int(w * 0.42), int(h * 0.48)
    draw.rectangle([wx1, wy1, wx2, wy2], fill="#C5D8E8", outline="#111111", width=3)

    if room.background == BackgroundKind.NIGHT_WINDOW:
        draw.rectangle([wx1 + 4, wy1 + 4, wx2 - 4, wy2 - 4], fill="#1A2030")
        draw.ellipse([wx2 - 80, wy1 + 20, wx2 - 40, wy1 + 60], fill="#F0E6B0", outline="#111111", width=2)
        if "lamp_dim" in room.wall_props:
            _draw_floor_lamp(draw, int(w * 0.78), int(h * 0.42), dim=True)
    elif room.background == BackgroundKind.MORNING_WINDOW:
        draw.rectangle([wx1 + 4, wy1 + 4, wx2 - 4, wy2 - 4], fill="#B8D4F0")
        draw.ellipse([wx1 + 30, wy1 + 25, wx1 + 70, wy1 + 65], fill="#FFE08A", outline="#111111", width=2)
    elif room.background == BackgroundKind.RAIN_WINDOW:
        draw.rectangle([wx1 + 4, wy1 + 4, wx2 - 4, wy2 - 4], fill="#8A9AAA")
        for i in range(8):
            x = wx1 + 20 + i * 35
            draw.line([(x, wy1 + 10), (x - 8, wy2 - 10)], fill="#667788", width=2)
    elif room.background == BackgroundKind.SUNDAY_GREY:
        draw.rectangle([wx1 + 4, wy1 + 4, wx2 - 4, wy2 - 4], fill="#9AA0A8")
        if "calendar" in room.wall_props:
            _draw_wall_calendar(draw, int(w * 0.52), int(h * 0.14), font_reg)
    elif room.background == BackgroundKind.WORK_DESK:
        draw.rectangle([wx1 + 4, wy1 + 4, wx2 - 4, wy2 - 4], fill="#A8B8C8")
        _draw_side_desk(draw, int(w * 0.72), int(h * 0.50))
    elif room.background == BackgroundKind.DOOR_TENSION:
        draw.rectangle([wx1 + 4, wy1 + 4, wx2 - 4, wy2 - 4], fill="#B0B8C0")
        _draw_door(draw, int(w * 0.55), int(h * 0.10), int(h * 0.42))
    elif room.background == BackgroundKind.PARTY_ENTRY:
        draw.rectangle([wx1 + 4, wy1 + 4, wx2 - 4, wy2 - 4], fill="#2A3040")
        _draw_door(draw, int(w * 0.50), int(h * 0.10), int(h * 0.40), party=True)
    elif room.background == BackgroundKind.CALM_LAMP:
        draw.rectangle([wx1 + 4, wy1 + 4, wx2 - 4, wy2 - 4], fill="#C8D0E0")
        _draw_floor_lamp(draw, int(w * 0.78), int(h * 0.40), dim=False)
    else:
        draw.rectangle([wx1 + 4, wy1 + 4, wx2 - 4, wy2 - 4], fill="#B8CCE0")

    if "plant" in room.wall_props:
        _draw_plant(draw, int(w * 0.86), int(h * 0.38))
    if "clock" in room.wall_props:
        _draw_wall_clock(draw, int(w * 0.48), int(h * 0.08))
    if "shelf" in room.wall_props:
        _draw_shelf(draw, int(w * 0.62), int(h * 0.22))


def draw_couch(draw, w: int, h: int) -> tuple[int, int]:
    """Same couch every frame. Returns seat center (cx, seat_y)."""
    left, top, right, seat_y = couch_bounds(w, h)
    back_h = int(h * 0.07)
    base_bot = seat_y + int(h * 0.04)
    draw.rounded_rectangle(
        [left, top, right, base_bot],
        radius=18,
        fill="#C4B8A8",
        outline="#111111",
        width=4,
    )
    draw.rounded_rectangle(
        [left, top, right, top + back_h],
        radius=14,
        fill="#B8A898",
        outline="#111111",
        width=3,
    )
    draw.line([(left + 20, seat_y), (right - 20, seat_y)], fill="#A09080", width=4)
    arm_w = int((right - left) * 0.08)
    arm_top = top + back_h
    arm_bot = seat_y + 12
    draw.rounded_rectangle(
        [left, arm_top, left + arm_w, arm_bot],
        radius=10,
        fill="#B0A090",
        outline="#111111",
        width=2,
    )
    draw.rounded_rectangle(
        [right - arm_w, arm_top, right, arm_bot],
        radius=10,
        fill="#B0A090",
        outline="#111111",
        width=2,
    )
    cx = (left + right) // 2
    return cx, seat_y - 20


def _draw_floor_lamp(draw, x: int, y: int, *, dim: bool) -> None:
    color = "#E8D8A0" if not dim else "#A09070"
    draw.line([(x, y + 80), (x, y + 200)], fill="#111111", width=4)
    draw.polygon([(x - 35, y), (x + 35, y), (x + 20, y + 50), (x - 20, y + 50)], fill=color, outline="#111111", width=2)


def _draw_plant(draw, x: int, y: int) -> None:
    draw.rectangle([x - 15, y + 40, x + 15, y + 90], fill="#8B7355", outline="#111111", width=2)
    draw.ellipse([x - 35, y, x + 35, y + 55], fill="#6A9A5B", outline="#111111", width=2)


def _draw_wall_clock(draw, x: int, y: int) -> None:
    draw.ellipse([x - 35, y, x + 35, y + 70], outline="#111111", width=3, fill="#FFFFFF")
    draw.line([(x, y + 35), (x, y + 15)], fill="#111111", width=3)
    draw.line([(x, y + 35), (x + 18, y + 35)], fill="#111111", width=2)


def _draw_wall_calendar(draw, x: int, y: int, font) -> None:
    draw.rectangle([x, y, x + 90, y + 70], fill="#FFFFFF", outline="#111111", width=3)
    draw.rectangle([x, y, x + 90, y + 22], fill="#CC4444", outline="#111111", width=2)
    draw.text((x + 8, y + 30), "SUN", fill="#111111", font=font)


def _draw_shelf(draw, x: int, y: int) -> None:
    draw.line([(x, y), (x + 120, y)], fill="#111111", width=4)
    draw.line([(x + 10, y), (x + 10, y + 60)], fill="#111111", width=3)
    draw.line([(x + 110, y), (x + 110, y + 60)], fill="#111111", width=3)
    draw.rectangle([x + 30, y - 25, x + 55, y - 5], fill="#8EB8FF", outline="#111111", width=2)


def _draw_door(draw, x: int, y: int, height: int, *, party: bool = False) -> None:
    fill = "#6A5040" if party else "#A09080"
    draw.rectangle([x, y, x + 100, y + height], fill=fill, outline="#111111", width=4)
    draw.ellipse([x + 78, y + height // 2, x + 90, y + height // 2 + 12], fill="#D4A830", outline="#111111", width=2)


def _draw_side_desk(draw, x: int, y: int) -> None:
    draw.rectangle([x, y, x + 140, y + 12], fill="#9A8A78", outline="#111111", width=3)
    draw.rectangle([x + 20, y - 50, x + 100, y], fill="#E0E0E0", outline="#111111", width=2)


def draw_foreground_prop(draw, cx: int, seat_y: int, prop: str | None) -> None:
    if prop == "laptop":
        lx = cx + 180
        draw.rectangle([lx, seat_y - 30, lx + 90, seat_y + 10], fill="#888888", outline="#111111", width=2)
        draw.rectangle([lx + 5, seat_y - 55, lx + 85, seat_y - 28], fill="#C0C0C0", outline="#111111", width=2)
    elif prop == "phone":
        px = cx + 150
        draw.rounded_rectangle([px, seat_y - 20, px + 40, seat_y + 50], radius=6, outline="#111111", width=3, fill="#222222")
