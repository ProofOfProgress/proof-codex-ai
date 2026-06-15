"""Tests for Mixamo client helpers."""

from shorts_bot.production.blender.mixamo_client import DEFAULT_PHASE_QUERIES, is_logged_in


def test_is_logged_in_false_on_landing():
    html = '<a href="#">Log in</a><a href="#">Sign up</a>'
    assert is_logged_in("https://www.mixamo.com/#/", html) is False


def test_is_logged_in_true_when_no_login_links():
    html = "<nav>Characters Animations</nav>"
    assert is_logged_in("https://www.mixamo.com/#/?type=Motion", html) is True


def test_default_phase_queries():
    assert "wave" in DEFAULT_PHASE_QUERIES
    assert "lunge" in DEFAULT_PHASE_QUERIES
