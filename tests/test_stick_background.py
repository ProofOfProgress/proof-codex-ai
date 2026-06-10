from pathlib import Path

from shorts_bot.production.image_prompts import segment_to_prompt
from shorts_bot.production.render_stickfigures import render_stick_frame
from shorts_bot.production.stick_background import BackgroundKind, plan_room
from shorts_bot.production.image_prompts import ImageBrief
from shorts_bot.production.turboscribe_parser import TranscriptSegment


def test_plan_room_night():
    room = plan_room("It's 3 AM and your brain won't stop")
    assert room.background == BackgroundKind.NIGHT_WINDOW
    assert "moon" in room.wall_props or "lamp_dim" in room.wall_props


def test_plan_room_sunday():
    room = plan_room("the minute before you open work email on Sunday")
    assert room.background == BackgroundKind.SUNDAY_GREY


def test_prompt_mentions_couch():
    p = segment_to_prompt(TranscriptSegment(0.0, "One breath before the text", "00.00"), topic="texts")
    assert "couch" in p.lower()
    assert "background" in p.lower()


def test_render_with_background(tmp_path: Path):
    brief = ImageBrief(0, 5, "00.00", "Sunday dread before opening email", "prompt")
    out = tmp_path / "00.00.png"
    assert render_stick_frame(brief, out)
    assert out.stat().st_size > 8000
