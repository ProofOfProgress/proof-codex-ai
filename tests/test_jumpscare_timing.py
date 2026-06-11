from shorts_bot.production.jumpscare_timing import (
    plan_for_draft,
    scare_sentence_indices,
    sting_start_seconds,
)


def test_profiles_rotate_by_draft_id():
    p2 = plan_for_draft(2, 10)
    p3 = plan_for_draft(3, 10)
    assert p2.profile != p3.profile or p2.primary_segment_index != p3.primary_segment_index


def test_early_snap_not_last_segment():
    plan = plan_for_draft(3, 10)  # draft 3 % 5 = mid_twist actually - let me check
    # draft_id 4 % 5 = 4 = double_tap
    plan = plan_for_draft(4, 10)
    assert plan.profile == "double_tap"
    assert plan.decoy_segment_index is not None
    assert plan.primary_segment_index == 9

    plan = plan_for_draft(3, 10)  # 3 % 5 = 3 = mid_twist
    assert plan.profile == "mid_twist"
    assert plan.primary_segment_index < 9


def test_sting_start_uses_segment_times():
    plan = plan_for_draft(2, 5)
    segments = [
        {"start_seconds": 0, "end_seconds": 5},
        {"start_seconds": 5, "end_seconds": 12},
        {"start_seconds": 12, "end_seconds": 20},
    ]
    t = sting_start_seconds(plan, segments=segments, total_duration=25.0)
    assert 0 <= t < 25.0


def test_scare_sentence_indices_double_tap():
    plan = plan_for_draft(4, 10)
    idx = scare_sentence_indices(plan, 10)
    assert len(idx) >= 2
