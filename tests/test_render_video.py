from shorts_bot.production.render_video import _scaled_durations


def test_scaled_durations_match_audio():
    segments = [
        {"start_seconds": 0, "end_seconds": 10},
        {"start_seconds": 10, "end_seconds": 30},
    ]
    durs = _scaled_durations(segments, 20.0)
    assert abs(sum(durs) - 20.0) < 0.01


def test_upload_title_not_clickbait():
    from shorts_bot.production.upload_meta import build_upload_package

    pkg = build_upload_package("cant sleep at 3am", "Stop scrolling", draft_id=6)
    assert "stop scrolling" not in pkg.title.lower()
    assert pkg.visibility == "unlisted"
