from pathlib import Path

from shorts_bot.production.image_prompts import ImageBrief
from shorts_bot.production.render_stickfigures import render_stick_frame
from shorts_bot.production.scene_plan import ai_likelihood_score, plan_scene


def test_plan_scene_phone_pose():
    p = plan_scene("Try this before you reach for your phone again.")
    assert p.pose.value in {"putting_phone_down", "reaching_phone"}


def test_ai_score_lower_for_casual():
    casual = "Okay it's 3 AM. I don't grab my phone. I just breathe. That's it."
    formal = "It is important to note that in today's fast-paced world one must delve into sleep hygiene."
    assert ai_likelihood_score(casual) < ai_likelihood_score(formal)


def test_render_stick_frame_writes_png(tmp_path: Path):
    brief = ImageBrief(0, 5, "00.00", "It's 3 AM and your brain is doing laps.", "prompt")
    out = tmp_path / "00.00.png"
    assert render_stick_frame(brief, out)
    assert out.stat().st_size > 5000
