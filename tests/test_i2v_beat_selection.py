from shorts_bot.production.render_ai_video import select_i2v_beat_indices


def test_all_beats_when_under_cap():
    assert select_i2v_beat_indices(8, 10) == list(range(8))


def test_hook_and_finale_always_included():
    indices = select_i2v_beat_indices(12, 6)
    assert indices[0] == 0
    assert indices[-1] == 11
    assert len(indices) == 6


def test_single_beat_is_hook():
    assert select_i2v_beat_indices(5, 1) == [0]


def test_two_beats_hook_and_finale():
    assert select_i2v_beat_indices(10, 2) == [0, 9]
