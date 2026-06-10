from pathlib import Path

from shorts_bot.production.image_prompts import ImageBrief, segment_to_prompt
from shorts_bot.production.render_stickfigures import render_stick_frame
from shorts_bot.production.stick_background import BackgroundKind, plan_room
from shorts_bot.production.turboscribe_parser import TranscriptSegment


def test_plan_room_night():
    room = plan_room("It's 3 AM and your brain won't stop")
    assert room.background == BackgroundKind.NIGHT_WINDOW
    assert room.furniture == "bed"


def test_plan_room_sunday():
    room = plan_room("the minute before you open work email on Sunday")
    assert room.background == BackgroundKind.SUNDAY_GREY
    assert "calendar" in room.wall_props


def test_plan_room_plain_minimal():
    room = plan_room("try this before you reply")
    assert room.background == BackgroundKind.PLAIN
    assert room.furniture is None
    assert room.wall_props == []


def test_prompt_chainsfr_minimal_not_couch_locked():
    p = segment_to_prompt(TranscriptSegment(0.0, "One breath before the text", "00.00"), topic="texts")
    assert "acting" in p.lower()
    assert "same couch" not in p.lower()
    assert "minimal" in p.lower()


def test_render_with_background(tmp_path: Path):
    brief = ImageBrief(0, 5, "00.00", "Sunday dread before opening email", "prompt")
    out = tmp_path / "00.00.png"
    assert render_stick_frame(brief, out)
    assert out.stat().st_size > 8000


def test_render_plain_standing(tmp_path: Path):
    brief = ImageBrief(0, 5, "00.00", "try this before you walk in alone", "prompt")
    out = tmp_path / "00.00.png"
    assert render_stick_frame(brief, out)
    assert out.stat().st_size > 5000
