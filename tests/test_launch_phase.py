"""Launch phase — first 3 Shorts: SFX yes, talking/subtitles no."""

from __future__ import annotations

from shorts_bot.config import Settings
from shorts_bot.production.horror_sfx_mix import build_sfx_cues
from shorts_bot.production.jumpscare_timing import JumpscarePlan
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


def test_kling_video_silent_during_launch_sfx_in_post():
    s = Settings(kling_generate_audio=True)
    assert kling_sound_enabled_for_draft(1) is False  # no Kling speech track


def test_launch_sfx_includes_flicker_cues():
    plan = JumpscarePlan(
        profile="finale",
        primary_segment_index=2,
        decoy_segment_index=None,
        has_jumpscare=True,
        sting_start_ratio=0.92,
        volume_warning="",
        creator_note="",
    )
    segments = [
        {"start_seconds": 0, "end_seconds": 10},
        {"start_seconds": 10, "end_seconds": 20},
        {"start_seconds": 20, "end_seconds": 30},
    ]
    cues = build_sfx_cues(segments, plan, audio_duration=30.0, draft_id=2)
    kinds = {c.kind for c in cues}
    assert "light_flicker" in kinds
    assert "stinger" in kinds


def test_kling_negative_bans_speech_on_launch():
    extra = kling_extra_negative_for_draft(1)
    assert "spoken dialogue" in extra
    assert kling_extra_negative_for_draft(5) == ""


def test_skip_narrator_on_launch():
    assert skip_narrator_tts(2) is True


def test_silent_kling_prompt_motion_and_form2():
    prompt = build_kling_prompt(
        "fog road",
        "Handheld POV on rural road.",
        part_index=1,
        total_parts=3,
        draft_id=2,
    )
    assert "NO HUMAN SPEECH" in prompt or "ABSOLUTELY NO HUMAN SPEECH" in prompt
    assert "flicker" in prompt.lower()
    assert "wave" in prompt.lower()
