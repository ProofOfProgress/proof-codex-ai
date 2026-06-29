"""Tests for TikTok Shop Content Policy text checks."""

from shorts_bot.tiktok_shop.tos_policy import check_promotional_text


def test_misinformation_sale_word_boundary():
    assert check_promotional_text("On sale now for kitchen fans")
    assert not check_promotional_text("Love this kitchen gadget for everyday use")


def test_no_false_positive_wholesale():
    # "sale" substring in wholesale should not trigger
    assert not check_promotional_text("Wholesale quality build")


def test_redirect_url_blocked():
    hits = check_promotional_text("Check https://evil.com for more")
    assert any("Redirect" in h for h in hits)


def test_phone_number_blocked():
    hits = check_promotional_text("Call me at 555-123-4567")
    assert any("phone" in h.lower() for h in hits)


def test_giveaway_blocked():
    hits = check_promotional_text("FREE GIFT if you comment to win")
    assert any("Giveaway" in h or "giveaway" in h.lower() for h in hits)


def test_weight_management_blocked():
    hits = check_promotional_text("This pill helps you lose weight fast")
    assert hits


def test_percent_off_regex():
    hits = check_promotional_text("Get 50% off today")
    assert any("%" in h or "Misinformation" in h for h in hits)


def test_clean_pain_point_hook():
    assert check_promotional_text("Tired of your phone sliding off the mount?") == []
