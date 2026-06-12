from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from shorts_bot.config import Settings
from shorts_bot.integrations.gmail_send import has_gmail_smtp, send_gmail_email
from shorts_bot.integrations.slack import post_slack_message, send_test_message, slack_can_post
from shorts_bot.integrations.slack_email import has_slack_email, post_slack_via_email
from shorts_bot.web.app import app


def _email_settings(**kwargs) -> Settings:
    base = dict(
        slack_channel_email="peripheral-ops@proofworkspace.slack.com",
        gmail_smtp_user="ops@gmail.com",
        gmail_smtp_app_password="abcdefghijklmnop",
        slack_notify_enabled=True,
        slack_post_mode="email",
    )
    base.update(kwargs)
    return Settings(**base)


def test_has_gmail_smtp():
    assert not has_gmail_smtp()


def test_has_slack_email_detects_config(monkeypatch):
    cfg = _email_settings()
    monkeypatch.setattr("shorts_bot.integrations.gmail_send.settings", cfg)
    monkeypatch.setattr("shorts_bot.integrations.slack_email.settings", cfg)
    assert has_slack_email()


@patch("shorts_bot.integrations.gmail_send.smtplib.SMTP")
def test_send_gmail_email(mock_smtp, monkeypatch):
    cfg = _email_settings()
    monkeypatch.setattr("shorts_bot.integrations.gmail_send.settings", cfg)
    client = mock_smtp.return_value.__enter__.return_value

    ok, err = send_gmail_email(
        to="peripheral-ops@proofworkspace.slack.com",
        subject="[Peripheral] test",
        body="hello",
    )
    assert ok
    assert err == ""
    client.starttls.assert_called_once()
    client.login.assert_called_once()
    client.sendmail.assert_called_once()


@patch("shorts_bot.integrations.slack_email.send_gmail_email", return_value=(True, ""))
def test_post_slack_via_email(mock_send, monkeypatch):
    cfg = _email_settings()
    monkeypatch.setattr("shorts_bot.integrations.slack_email.settings", cfg)
    monkeypatch.setattr("shorts_bot.integrations.gmail_send.settings", cfg)

    assert post_slack_via_email("pipeline ok", event="daily")
    mock_send.assert_called_once()
    args, kwargs = mock_send.call_args
    assert kwargs["to"] == cfg.slack_channel_email
    assert "[daily]" in kwargs["subject"]


@patch("shorts_bot.integrations.slack_email.post_slack_via_email", return_value=True)
def test_post_slack_message_email_mode(mock_email, monkeypatch):
    cfg = _email_settings()
    monkeypatch.setattr("shorts_bot.integrations.slack.settings", cfg)
    monkeypatch.setattr("shorts_bot.integrations.slack_email.settings", cfg)

    assert post_slack_message("alert", event="test")
    mock_email.assert_called_once()


@patch("shorts_bot.integrations.slack_email.post_slack_via_email", return_value=True)
def test_slack_can_post_with_email_only(mock_email, monkeypatch):
    cfg = _email_settings()
    monkeypatch.setattr("shorts_bot.integrations.slack.settings", cfg)
    monkeypatch.setattr("shorts_bot.integrations.slack_email.settings", cfg)
    monkeypatch.setattr("shorts_bot.integrations.gmail_send.settings", cfg)
    assert slack_can_post()


@patch("shorts_bot.integrations.slack_email.post_slack_via_email", return_value=True)
def test_send_test_message_via_email(mock_post, monkeypatch):
    cfg = _email_settings()
    monkeypatch.setattr("shorts_bot.integrations.slack.settings", cfg)
    monkeypatch.setattr("shorts_bot.integrations.slack_email.settings", cfg)
    monkeypatch.setattr("shorts_bot.integrations.gmail_send.settings", cfg)

    ok, msg = send_test_message()
    assert ok
    assert "Gmail" in msg


def test_slack_status_includes_email():
    r = TestClient(app).get("/api/slack/status")
    assert r.status_code == 200
    assert "email" in r.json()
    assert r.json()["email"]["doc"] == "docs/FOR_OWNER_SLACK_EMAIL.md"
