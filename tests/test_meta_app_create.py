"""Tests for Meta app creation helpers."""

from __future__ import annotations

from unittest.mock import MagicMock

from shorts_bot.integrations.meta_app_create import _password_modal_visible


def test_password_modal_visible_detects_reenter():
    page = MagicMock()
    page.inner_text.return_value = "Please re-enter your password to continue"
    assert _password_modal_visible(page) is True


def test_password_modal_not_visible_on_explorer():
    page = MagicMock()
    page.inner_text.return_value = "Graph API Explorer — Get Token"
    assert _password_modal_visible(page) is False
