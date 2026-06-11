from shorts_bot.production.jumpscare_timing import (
    plan_for_draft,
    scare_sentence_indices,
    sting_start_seconds,
)


def test_finale_is_default_majority():
    plans = [plan_for_draft(i, 9) for i in range(1, 10) if i % 3 != 0]
    assert all(p.profile == "finale" for p in plans)
    assert all(p.has_jumpscare for p in plans)
    assert all(p.primary_segment_index == 8 for p in plans)


def test_suspense_replay_every_third_draft():
    plan = plan_for_draft(3, 9)
    assert plan.profile == "suspense_replay"
    assert not plan.has_jumpscare
    assert plan.volume_warning == ""


def test_sting_start_couple_seconds_before_end():
    plan = plan_for_draft(5, 9)  # finale
    t = sting_start_seconds(plan, segments=[], total_duration=27.4)
    assert t is not None
    assert 24.0 <= t <= 26.0


def test_sting_aligns_to_finale_segment_flash():
    plan = plan_for_draft(5, 9)
    segments = [
        {"start_seconds": 0.0, "end_seconds": 20.0},
        {"start_seconds": 20.0, "end_seconds": 27.4},
    ]
    plan = plan.__class__(
        profile=plan.profile,
        primary_segment_index=1,
        decoy_segment_index=None,
        has_jumpscare=True,
        sting_start_ratio=plan.sting_start_ratio,
        volume_warning=plan.volume_warning,
        creator_note=plan.creator_note,
    )
    t = sting_start_seconds(plan, segments=segments, total_duration=27.4)
    assert t is not None
    # flash at 27.12 (27.4 - 0.28), sting ~0.06s before
    assert 26.9 <= t <= 27.15


def test_no_sting_on_suspense_replay():
    plan = plan_for_draft(3, 9)
    assert sting_start_seconds(plan, segments=[], total_duration=27.4) is None


def test_scare_sentence_only_finale_last():
    finale = plan_for_draft(5, 9)
    replay = plan_for_draft(3, 9)
    assert scare_sentence_indices(finale, 8) == {7}
    assert scare_sentence_indices(replay, 8) == set()
