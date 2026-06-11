from shorts_bot.production.screen_text_spec import (
    extract_time_label,
    infer_overlay_from_beat,
    infer_overlay_from_spoken,
    overlays_for_segments,
)

DRAFT_3_SEGMENTS = [
    {"spoken_text": "Your security camera flag motion at 3:12 AM."},
    {"spoken_text": "You live alone. You open the app."},
    {"spoken_text": "The hallway was empty. You told yourself it was a glitch."},
    {"spoken_text": "You refreshed the feed. The figure was closer."},
    {"spoken_text": "You checked the locks, all sealed."},
    {"spoken_text": "You heard a soft tap from the speaker."},
    {"spoken_text": "The live view updated. Something stood at the bottom"},
    {"spoken_text": "of your bed, staring into the lens."},
    {"spoken_text": "It smiled. Then it lunged at the camera."},
]


def test_extract_time_from_hook():
    assert "3:12" in extract_time_label("", "Motion at 3:12 AM — you live alone")


def test_phone_motion_beat_is_in_phone_feed():
    ov = infer_overlay_from_beat(
        "Phone screen: security app motion alert 3:12 AM, dark apartment",
        hook="Your security camera flagged motion at 3:12 AM",
        topic="security camera motion",
    )
    assert ov is not None
    assert ov.kind == "phone_feed"
    assert ov.feed_state == "motion_banner"
    assert "3:12" in ov.time_label


def test_cctv_hud_from_live_feed_beat():
    ov = infer_overlay_from_beat(
        "Live feed hallway empty — timestamp overlay",
        hook="3:12 AM alert",
        topic="security camera",
    )
    assert ov is not None
    assert ov.kind == "phone_feed"
    assert ov.feed_state == "empty"


def test_message_bubble_from_delivered_beat():
    ov = infer_overlay_from_beat(
        "New message slides in: I can see you",
        topic="text delivered phone off",
        spoken_text="I can see you",
    )
    assert ov is not None
    assert ov.kind == "message_bubble"
    assert "see you" in ov.primary.lower()


def test_spoken_overlay_draft3_segments():
    hook = "Your security camera flagged motion at 3:12 AM — you live alone."
    topic = "security camera motion"
    kinds = []
    for seg in DRAFT_3_SEGMENTS:
        ov = infer_overlay_from_spoken(seg["spoken_text"], hook=hook, topic=topic)
        kinds.append(ov.kind if ov else None)
    assert kinds[0] == "cctv_hud"
    assert kinds[1] == "phone_feed"
    assert kinds[5] == "phone_feed"
    specs = overlays_for_segments(
        DRAFT_3_SEGMENTS,
        visual_beats=["wrong"] * 8,
        hook=hook,
        topic=topic,
    )
    assert specs[1].feed_state == "app_opening"
    assert specs[2] is not None and specs[2].feed_state == "empty"
    assert specs[3] is not None and specs[3].feed_state == "figure_closer"
    assert specs[5].feed_state == "live_audio"
    assert specs[4] is None
    assert specs[8] is None


def test_overlays_for_segments_maps_beats():
    segments = [
        {"spoken_text": "You opened the app."},
        {"spoken_text": "The hallway was empty."},
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
    assert specs[0] is not None and specs[0].kind == "phone_feed"
    assert specs[1] is not None and specs[1].kind == "phone_feed"
