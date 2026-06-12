"""Shared pytest fixtures — isolate tests from developer .env."""

from __future__ import annotations

import pytest

from shorts_bot.config import Settings

_SLACK_MODULES = (
    "shorts_bot.integrations.slack",
    "shorts_bot.integrations.slack_email",
    "shorts_bot.integrations.gmail_send",
)


@pytest.fixture
def no_slack_config(monkeypatch):
    """No webhook, bot, or email — Slack posts are no-ops."""
    return patch_slack_settings(
        monkeypatch,
        slack_webhook_url=None,
        slack_bot_token=None,
        slack_channel_id=None,
        slack_channel_email=None,
        gmail_smtp_user=None,
        gmail_smtp_app_password=None,
        slack_post_mode="bot",
        slack_notify_enabled=True,
    )


def patch_slack_settings(monkeypatch, **kwargs) -> Settings:
    """Apply the same Settings to all Slack integration modules."""
    cfg = Settings(**kwargs)
    for mod in _SLACK_MODULES:
        monkeypatch.setattr(f"{mod}.settings", cfg)
    return cfg
