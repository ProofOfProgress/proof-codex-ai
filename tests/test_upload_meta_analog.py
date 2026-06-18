from shorts_bot.production.upload_meta import (
    HORROR_BACKEND_TAGS,
    _tags_from_research,
    _topic_hashtags,
    build_upload_package,
)


class _FakeResearch:
    keyword_insights = []


class _StaleEyeResearch:
    title_formula = "🔊 VOLUME WARNING: The Eye Found Me in My Dreams. #horror #shorts"
    keyword_insights = [
        {"keyword": "the eye"},
        {"keyword": "theeye"},
        {"keyword": "security camera horror"},
    ]


def test_backend_tags_include_analog_horror():
    assert "analog horror" in HORROR_BACKEND_TAGS
    assert "found footage" in HORROR_BACKEND_TAGS


def test_cctv_topic_hashtags_analog_not_phone():
    tags = _topic_hashtags("security camera flagged motion at 3:12 AM")
    assert "#AnalogHorror" in tags
    assert "#PhoneHorror" not in tags
    assert "#SecurityCamera" in tags


def test_text_topic_skips_phone_hashtag_when_phones_disabled():
    tags = _topic_hashtags("wrong text message delivered while phone off")
    assert "#PhoneHorror" not in tags
    assert "#AnalogHorror" in tags


def test_tags_from_research_cctv_surveillance():
    tags = _tags_from_research("security camera motion alone", _FakeResearch())
    lower = {t.lower() for t in tags}
    assert "security camera horror" in lower
    assert "surveillance horror" in lower


def test_upload_package_security_cam_topic():
    pkg = build_upload_package(
        "security camera motion alone",
        "Your security camera flagged motion at 3:12 AM.",
        draft_id=3,
    )
    assert "analog horror" in {t.lower() for t in pkg.tags}


def test_security_cam_rejects_off_lane_research_title():
    pkg = build_upload_package(
        "security camera motion alone",
        "Your security camera flagged motion at 3:12 AM.",
        draft_id=3,
        research=_StaleEyeResearch(),
    )
    assert "security camera" in pkg.title.lower()
    assert "eye" not in pkg.title.lower()
    lower_tags = {t.lower() for t in pkg.tags}
    assert "the eye" not in lower_tags
    assert "theeye" not in lower_tags
