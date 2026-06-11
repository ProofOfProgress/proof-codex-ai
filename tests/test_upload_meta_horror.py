from shorts_bot.production.upload_meta import _normalize_horror_hook, _safe_description


def test_normalize_first_person_hook():
    assert "Your" in _normalize_horror_hook("My security camera flagged motion", "topic")
    assert "you live alone" in _normalize_horror_hook("I live alone", "topic").lower()


def test_description_uses_normalized_hook():
    desc = _safe_description("security cam", "My camera flagged motion — I live alone.")
    assert "Your" in desc or "your" in desc
    assert "competitor" not in desc.lower()
