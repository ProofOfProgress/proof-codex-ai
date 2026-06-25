from shorts_bot.youtube.post_upload import (
    DEFAULT_CTA,
    _cta_is_safe,
    pick_cta_comment,
)


def test_default_cta_simple_and_safe():
    lower = DEFAULT_CTA.lower()
    assert "jumpscare" not in lower
    assert "impossible detail" not in lower
    assert "scary story" in lower
    assert _cta_is_safe(DEFAULT_CTA)


def test_pick_cta_rotation_safe():
    for i in range(1, 12):
        cta = pick_cta_comment(draft_id=i)
        assert _cta_is_safe(cta)
        assert "impossible detail" not in cta.lower()


def test_unsafe_cta_rejected():
    assert not _cta_is_safe("🔊 jumpscare at the end — headphones!")
    assert not _cta_is_safe("scare at the end watch out")
    assert not _cta_is_safe("What impossible detail next?")
