from shorts_bot.drafts.meta import visual_beat_for_segment


def test_visual_beat_maps_first_and_last():
    beats = ["hook shot", "middle", "finale"]
    assert visual_beat_for_segment(beats, 0, 5) == "hook shot"
    assert visual_beat_for_segment(beats, 4, 5) == "finale"


def test_visual_beat_none_when_empty():
    assert visual_beat_for_segment(None, 0, 3) is None
    assert visual_beat_for_segment([], 0, 3) is None
