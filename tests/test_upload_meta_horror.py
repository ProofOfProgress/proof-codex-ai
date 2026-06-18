from shorts_bot.production.description_copy import (
    FINALE_VOLUME_WARNING,
    description_is_safe,
    sanitize_description_text,
)
from shorts_bot.production.upload_meta import _normalize_horror_hook, _safe_description


def test_normalize_first_person_hook():
    assert "Your" in _normalize_horror_hook("My security camera flagged motion", "topic")
    assert "you live alone" in _normalize_horror_hook("I live alone", "topic").lower()


def test_description_uses_normalized_hook():
    desc = _safe_description("security cam", "My camera flagged motion — I live alone.")
    assert "Your" in desc or "your" in desc
    assert "competitor" not in desc.lower()


def test_description_uses_plain_language():
    for draft_id in range(1, 12):
        desc = _safe_description(
            "security camera motion",
            "Your security camera flagged motion at 3:12 AM.",
            draft_id=draft_id,
        )
        assert description_is_safe(desc), desc
        lower = desc.lower()
        assert "impossible detail" not in lower
        assert "micro-story" not in lower
        assert "terrifying faceless" not in lower


def test_finale_description_says_jumpscare():
    desc = _safe_description(
        "security camera motion",
        "Your security camera flagged motion at 3:12 AM.",
        draft_id=1,
    )
    assert "jumpscare" in desc.lower()


def test_sanitize_upgrades_legacy_copy():
    raw = "🔊 VOLUME WARNING — loud moment at the end. Headphones advised."
    clean = sanitize_description_text(raw)
    assert "jumpscare" in clean.lower()
    assert "loud moment" not in clean.lower()
    assert description_is_safe(clean)


def test_sanitize_strips_impossible_detail_tease():
    raw = "One impossible detail → tension → watch to the end."
    clean = sanitize_description_text(raw)
    assert "impossible detail" not in clean.lower()
    assert description_is_safe(clean)


def test_volume_warning_plain_wording():
    assert "jumpscare" in FINALE_VOLUME_WARNING.lower()
    assert "impossible" not in FINALE_VOLUME_WARNING.lower()


def test_sanitize_does_not_duplicate_jumpscare():
    clean = sanitize_description_text("🔊 VOLUME WARNING — jumpscare at the end. Use headphones.")
    assert "jumpjumpjumpscare" not in clean.lower()
    assert clean.lower().count("jumpscare") == 1
