"""Micro jumpscare format — 3s lunge + volume sting."""

from shorts_bot.production.content_format import profile_for


def test_micro_jumpscare_profile():
    prof = profile_for("micro_jumpscare")
    assert prof.id == "micro_jumpscare"
    assert prof.max_i2v_beats == 0
    assert prof.target_duration_seconds[1] <= 4.0
