from shorts_bot.production.capcut_sfx import build_capcut_sfx_markdown


def test_finale_profile_includes_stinger_timing():
    segments = [
        {"start_seconds": 0, "spoken_text": "Hook line."},
        {"start_seconds": 5, "spoken_text": "Escalation."},
        {"start_seconds": 22, "spoken_text": "It lunged."},
    ]
    md = build_capcut_sfx_markdown(
        segments,
        topic="security cam",
        jumpscare_plan={"profile": "finale", "has_jumpscare": True},
        audio_duration=27.4,
    )
    assert "finale" in md
    assert "stinger" in md.lower()
    assert "24." in md or "25." in md  # ~27.4 - 2.5


def test_suspense_replay_skips_stinger():
    segments = [
        {"start_seconds": 0, "spoken_text": "Hook."},
        {"start_seconds": 24, "spoken_text": "Still watching."},
    ]
    md = build_capcut_sfx_markdown(
        segments,
        topic="mirror",
        jumpscare_plan={"profile": "suspense_replay", "has_jumpscare": False},
        audio_duration=28.0,
    )
    assert "suspense_replay" in md
    assert "No stinger" in md
