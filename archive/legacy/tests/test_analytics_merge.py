from shorts_bot.youtube.analytics_merge import merge_metrics


def test_merge_preserves_studio_swipe():
    existing = {
        "video_id": "abc",
        "viewed_vs_swiped_away": 72,
        "swipe_source": "studio",
    }
    incoming = {
        "video_id": "abc",
        "views": 1000,
        "average_view_percentage": 55,
        "swipe_source": "unavailable",
    }
    merged = merge_metrics(existing, incoming)
    assert merged["viewed_vs_swiped_away"] == 72
    assert merged["swipe_source"] == "studio"
    assert merged["average_view_percentage"] == 55


def test_merge_uses_video_id_label():
    merged = merge_metrics(None, {"video_id": "xyz", "views": 1})
    assert merged["video_label"] == "xyz"
