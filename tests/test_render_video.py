from shorts_bot.production.render_video import _jumpscare_video_filter, _scaled_durations
from shorts_bot.production.segment_sync import normalize_segment_timeline


def test_scaled_durations_after_normalize_match_audio():
    segments = [
        {"start_seconds": 1.0, "end_seconds": 10.0},
        {"start_seconds": 10.0, "end_seconds": 30.0},
    ]
    normed = normalize_segment_timeline(segments, 20.0)
    durs = _scaled_durations(normed, 20.0)
    assert abs(sum(durs) - 20.0) < 0.01


def test_jumpscare_filter_includes_zoom_and_flash():
    vf = _jumpscare_video_filter(3.0, width=1080, height=1920)
    assert "zoompan" in vf
    assert "eq=brightness" in vf


def test_scaled_durations_match_audio():
    segments = [
        {"start_seconds": 0, "end_seconds": 10},
        {"start_seconds": 10, "end_seconds": 30},
    ]
    durs = _scaled_durations(segments, 20.0)
    assert abs(sum(durs) - 20.0) < 0.01


def test_upload_title_not_clickbait(monkeypatch):
    from shorts_bot.config import settings as cfg
    from shorts_bot.production.upload_meta import build_upload_package

    monkeypatch.setattr(cfg, "youtube_upload_visibility", "public")
    pkg = build_upload_package("cant sleep at 3am", "Stop scrolling", draft_id=6)
    assert "stop scrolling" not in pkg.title.lower()
    assert pkg.visibility == "public"
