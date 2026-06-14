"""Tests for phase motion prompts."""

from shorts_bot.production.blender.phase_motion_prompts import (
    english_prompt,
    mixamo_query,
    phase_queries_for_draft,
)


def test_draft_2_wave_prompt():
    assert "wave" in english_prompt(2, "wave").lower()
    assert mixamo_query(2, "wave") == "waving"


def test_draft_2_queries():
    q = phase_queries_for_draft(2)
    assert q["open"] == "zombie walk"
    assert q["lunge"] == "zombie attack"
