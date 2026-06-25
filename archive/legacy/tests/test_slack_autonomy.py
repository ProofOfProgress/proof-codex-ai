from __future__ import annotations

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from shorts_bot.config import Settings
from shorts_bot.integrations.slack_autonomy import (
    AUTONOMY_PREFIX,
    handle_slack_event,
    parse_slack_command,
    post_autonomy_command,
    strip_autonomy_prefix,
)
from shorts_bot.web.app import app


def _autonomy_settings(**kwargs) -> Settings:
    base = dict(
        slack_bot_token="xoxb-test-token",
        slack_channel_id="C0123456789",
        slack_app_token="xapp-test-token",
        slack_autonomy_enabled=True,
        slack_notify_enabled=True,
    )
    base.update(kwargs)
    return Settings(**base)


def test_strip_autonomy_prefix():
    assert strip_autonomy_prefix("[autonomy] status") == "status"
    assert strip_autonomy_prefix("[AUTONOMY] help") == "help"
    assert strip_autonomy_prefix("plain") is None


def test_parse_self_talk_command(monkeypatch):
    monkeypatch.setattr("shorts_bot.integrations.slack_autonomy.settings", _autonomy_settings())
    event = {
        "channel": "C0123456789",
        "text": f"{AUTONOMY_PREFIX} status",
        "bot_id": "B123",
        "ts": "1.0",
    }
    assert parse_slack_command(event, bot_user_id="U999") == "status"


def test_parse_ignores_wrong_channel(monkeypatch):
    monkeypatch.setattr("shorts_bot.integrations.slack_autonomy.settings", _autonomy_settings())
    event = {"channel": "COTHER", "text": "[autonomy] status", "ts": "2.0"}
    assert parse_slack_command(event) is None


def test_parse_owner_plain_message(monkeypatch):
    monkeypatch.setattr(
        "shorts_bot.integrations.slack_autonomy.settings",
        _autonomy_settings(slack_autonomy_owner_commands=True),
    )
    event = {
        "channel": "C0123456789",
        "user": "UOWNER",
        "text": "pending",
        "ts": "3.0",
    }
    assert parse_slack_command(event, bot_user_id="UBOT") == "pending"


@patch("shorts_bot.integrations.slack_autonomy.execute_slack_command", return_value="OK: 2 drafts")
def test_handle_slack_event_replies(mock_exec, monkeypatch):
    monkeypatch.setattr("shorts_bot.integrations.slack_autonomy.settings", _autonomy_settings())
    event = {
        "channel": "C0123456789",
        "text": "[autonomy] status",
        "ts": "4.0",
    }
    reply = handle_slack_event(event)
    assert reply == "OK: 2 drafts"
    mock_exec.assert_called_once_with("status")


@patch("shorts_bot.integrations.slack_autonomy.execute_slack_command", return_value="local ok")
@patch("shorts_bot.integrations.slack.post_slack_message", return_value=True)
@patch("shorts_bot.integrations.slack.post_slack_thread", return_value=True)
def test_post_autonomy_fallback_local(mock_thread, mock_post, mock_exec, monkeypatch):
    cfg = _autonomy_settings(slack_app_token=None)
    monkeypatch.setattr("shorts_bot.integrations.slack_autonomy.settings", cfg)
    monkeypatch.setattr("shorts_bot.integrations.slack.settings", cfg)
    ok, msg = post_autonomy_command("status")
    assert ok
    mock_post.assert_called_once()
    mock_exec.assert_called_once_with("status")
    mock_thread.assert_called_once()
    assert "socket mode off" in msg.lower()


@patch("shorts_bot.integrations.slack.post_slack_message", return_value=True)
def test_post_autonomy_bus_only(mock_post, monkeypatch):
    cfg = _autonomy_settings()
    monkeypatch.setattr("shorts_bot.integrations.slack_autonomy.settings", cfg)
    monkeypatch.setattr("shorts_bot.integrations.slack.settings", cfg)
    ok, msg = post_autonomy_command("help")
    assert ok
    assert "[autonomy]" in mock_post.call_args[0][0]
    assert "socket listener" in msg.lower()


def test_slack_autonomy_api(monkeypatch):
    monkeypatch.setattr(
        "shorts_bot.integrations.slack_autonomy.post_autonomy_command",
        lambda *a, **k: (True, "queued"),
    )
    r = TestClient(app).post("/api/slack/autonomy", json={"command": "status"})
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_slack_status_includes_autonomy():
    r = TestClient(app).get("/api/slack/status")
    assert r.status_code == 200
    assert "autonomy" in r.json()
    assert r.json()["autonomy"]["prefix"] == "[autonomy]"
