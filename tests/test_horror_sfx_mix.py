from shorts_bot.production.horror_sfx_mix import build_sfx_cues
from shorts_bot.production.jumpscare_timing import plan_for_draft


def test_finale_cues_include_stinger():
    segments = [
        {"start_seconds": 0, "spoken_text": "hook"},
        {"start_seconds": 10, "spoken_text": "escalation"},
        {"start_seconds": 22, "spoken_text": "lunge"},
    ]
    plan = plan_for_draft(5, 3)
    cues = build_sfx_cues(segments, plan, audio_duration=27.0)
    kinds = [c.kind for c in cues]
    assert "cam_alert" in kinds
    assert "stinger" in kinds
    assert "stinger_noise" in kinds


def test_suspense_replay_no_stinger():
    plan = plan_for_draft(3, 3)
    segments = [{"start_seconds": 0}, {"start_seconds": 20}]
    cues = build_sfx_cues(segments, plan, audio_duration=28.0)
    assert "stinger" not in [c.kind for c in cues]
