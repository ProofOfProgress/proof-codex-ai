from shorts_bot.production.screen_text_spec import (
    extract_time_label,
    infer_overlay_from_beat,
    overlays_for_segments,
)


def test_extract_time_from_hook():
    assert "3:12" in extract_time_label("", "Motion at 3:12 AM — you live alone")


def test_phone_alert_from_visual_beat():
    ov = infer_overlay_from_beat(
        "Phone screen: security app motion alert 3:12 AM, dark apartment",
        hook="Your security camera flagged motion at 3:12 AM",
        topic="security camera motion",
    )
    assert ov is not None
    assert ov.kind == "phone_alert"
    assert ov.primary == "Motion Detected"
    assert "3:12" in ov.time_label


def test_cctv_hud_from_live_feed_beat():
    ov = infer_overlay_from_beat(
        "Live feed hallway empty — timestamp overlay",
        hook="3:12 AM alert",
        topic="security camera",
    )
    assert ov is not None
    assert ov.kind == "cctv_hud"
    assert ov.primary == "● REC"


def test_message_bubble_from_delivered_beat():
    ov = infer_overlay_from_beat(
        "New message slides in: I can see you",
        topic="text delivered phone off",
        spoken_text="I can see you",
    )
    assert ov is not None
    assert ov.kind == "message_bubble"
    assert "see you" in ov.primary.lower()


def test_overlays_for_segments_maps_beats():
    segments = [
        {"spoken_text": "hook"},
        {"spoken_text": "hallway empty"},
    ]
    beats = [
        "Phone screen: security app motion alert 3:12 AM",
        "Live feed hallway empty — timestamp overlay",
    ]
    specs = overlays_for_segments(
        segments,
        visual_beats=beats,
        hook="3:12 AM",
        topic="security camera",
    )
    assert specs[0] is not None and specs[0].kind == "phone_alert"
    assert specs[1] is not None and specs[1].kind == "cctv_hud"
