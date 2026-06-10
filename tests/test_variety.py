from shorts_bot.production.variety import variety_for_draft


def test_variety_differs_by_draft_id():
    a = variety_for_draft(3)
    b = variety_for_draft(7)
    assert a.zoom_motion != b.zoom_motion or a.caption_y_offset != b.caption_y_offset


def test_variety_summary_includes_draft():
    v = variety_for_draft(12)
    assert "d12" in v.summary()
