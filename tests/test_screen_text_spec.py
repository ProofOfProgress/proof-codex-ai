from shorts_bot.production.screen_text_spec import (
    extract_time_label,
    infer_overlay_from_beat,
    infer_overlay_from_spoken,
    is_cctv_topic,
    overlays_for_segments,
    phone_screens_enabled,
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


def test_phone_screens_disabled_by_default():
    assert phone_screens_enabled() is False


def test_extract_time_from_hook():
    assert "3:12" in extract_time_label("", "Motion at 3:12 AM — you live alone")


def test_cctv_topic_detection():
    assert is_cctv_topic("your security camera flagged motion")
    assert not is_cctv_topic("mirror blink reflection")


def test_cctv_beat_is_hud_not_phone():
    ov = infer_overlay_from_beat(
        "Fullscreen CCTV hallway night vision, motion alert",
        hook="Your security camera flagged motion at 3:12 AM",
        topic="security camera motion",
    )
    assert ov is not None
    assert ov.kind == "cctv_hud"
    assert ov.primary == "REC"
    assert "3:12" in ov.secondary


def test_alarm_clock_from_nightstand_beat():
    ov = infer_overlay_from_beat(
        "POV door deadbolt, alarm clock on nightstand red digits 3:12 AM",
        topic="security camera",
    )
    assert ov is not None
    assert ov.kind == "alarm_clock"


def test_spoken_overlay_draft3_no_phones():
    hook = "Your security camera flagged motion at 3:12 AM — you live alone."
    topic = "security camera motion"
    kinds = []
    for seg in DRAFT_3_SEGMENTS:
        ov = infer_overlay_from_spoken(seg["spoken_text"], hook=hook, topic=topic)
        kinds.append(ov.kind if ov else None)
    assert kinds[0] == "alarm_clock"
    assert kinds[1] == "cctv_hud"
    assert kinds[3] == "cctv_hud"
    assert kinds[3] and kinds[3] != "phone_feed"
    assert kinds[4] == "alarm_clock"
    assert kinds[5] == "cctv_hud"
    assert kinds[6] == "cctv_hud"
    assert kinds[8] is None
    assert "phone_feed" not in kinds


def test_overlays_for_segments_cctv_only():
    segments = [
        {"spoken_text": "You opened the app."},
        {"spoken_text": "The hallway was empty."},
    ]
    beats = [
        "Fullscreen CCTV hallway POV night vision",
        "Fullscreen CCTV empty hallway",
    ]
    specs = overlays_for_segments(
        segments,
        visual_beats=beats,
        hook="3:12 AM",
        topic="security camera",
    )
    assert specs[0] is not None and specs[0].kind == "cctv_hud"
    assert specs[1] is not None and specs[1].kind == "cctv_hud"
