"""Launch phase — first 3 Shorts: SFX yes, talking/subtitles no."""

from __future__ import annotations

from shorts_bot.config import Settings
from shorts_bot.production.launch_phase import (
    is_silent_launch_draft,
    kling_extra_negative_for_draft,
    kling_sound_enabled_for_draft,
    should_burn_subtitles,
    skip_narrator_tts,
)
from shorts_bot.production.render_kling import build_kling_prompt


def test_silent_launch_drafts_1_through_3():
    assert is_silent_launch_draft(1) is True
    assert is_silent_launch_draft(3) is True
    assert is_silent_launch_draft(4) is False


def test_no_subtitles_during_launch():
    assert should_burn_subtitles(2) is False
    assert should_burn_subtitles(4) is True


def test_kling_sound_stays_on_during_launch():
    s = Settings(kling_generate_audio=True)
    assert kling_sound_enabled_for_draft(1) is True


def test_kling_negative_bans_speech_on_launch():
    extra = kling_extra_negative_for_draft(1)
    assert "spoken dialogue" in extra
    assert kling_extra_negative_for_draft(5) == ""


def test_skip_narrator_on_launch():
    assert skip_narrator_tts(2) is True


def test_silent_kling_prompt_has_ambient_not_dialogue():
    prompt = build_kling_prompt(
        "fog road",
        "I slow my car. Something moves in the ditch.",
        part_index=0,
        total_parts=3,
        draft_id=1,
    )
    assert "NO SPOKEN DIALOGUE" in prompt
    assert "wind" in prompt.lower()
    assert "quotes" not in prompt.lower() or "no quoted speech" in prompt.lower()
