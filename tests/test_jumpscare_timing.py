from shorts_bot.production.jumpscare_timing import (
    JumpscarePlan,
    plan_for_draft,
    scare_sentence_indices,
    sting_start_seconds,
)


def test_jumpscare_retired_stubs():
    plan = plan_for_draft(5, 9)
    assert not plan.has_jumpscare
    assert scare_sentence_indices(plan) == []
    assert sting_start_seconds(plan) == 0.0


def test_jumpscare_plan_from_dict():
    plan = JumpscarePlan.from_dict({"has_jumpscare": True, "primary_segment_index": 3})
    assert plan.has_jumpscare
    assert plan.scare_sentence_index == 3
