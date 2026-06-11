from shorts_bot.youtube.post_upload import (
    DEFAULT_CTA,
    _cta_is_safe,
    pick_cta_comment,
)


def test_default_cta_never_spoils_jumpscare():
    assert "jumpscare" not in DEFAULT_CTA.lower()
    assert "end" not in DEFAULT_CTA.lower() or "impossible" in DEFAULT_CTA.lower()
    assert _cta_is_safe(DEFAULT_CTA)


def test_pick_cta_rotation_safe():
    for i in range(1, 12):
        assert _cta_is_safe(pick_cta_comment(draft_id=i))


def test_unsafe_cta_rejected():
    assert not _cta_is_safe("🔊 jumpscare at the end — headphones!")
    assert not _cta_is_safe("scare at the end watch out")
