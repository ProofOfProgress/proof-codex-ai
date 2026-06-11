from shorts_bot.production.description_copy import (
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


def test_description_never_spoils_jumpscare():
    for draft_id in range(1, 12):
        desc = _safe_description(
            "security camera motion",
            "Your security camera flagged motion at 3:12 AM.",
            draft_id=draft_id,
        )
        assert description_is_safe(desc), desc
        assert "jumpscare" not in desc.lower()


def test_sanitize_strips_legacy_volume_warning():
    raw = "🔊 VOLUME WARNING — jumpscare near the end. Headphones advised."
    clean = sanitize_description_text(raw)
    assert "jumpscare" not in clean.lower()
    assert "end" in clean.lower()
    assert description_is_safe(clean)
