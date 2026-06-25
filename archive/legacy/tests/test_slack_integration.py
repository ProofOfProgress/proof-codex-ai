from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from shorts_bot.automation.alerts import record_automation_alert
from shorts_bot.config import Settings
from shorts_bot.integrations.slack import (
    has_slack_bot,
    has_slack_webhook,
    notify_automation_alert,
    post_slack_message,
    slack_setup_status,
)
from shorts_bot.web.app import app
from tests.conftest import patch_slack_settings


def test_has_slack_webhook_false_by_default(monkeypatch):
    monkeypatch.setattr(
        "shorts_bot.integrations.slack.settings",
        Settings(slack_webhook_url=None),
    )
    assert not has_slack_webhook()


def test_has_slack_webhook_detects_valid_url(monkeypatch):
    monkeypatch.setattr(
        "shorts_bot.integrations.slack.settings",
        Settings(slack_webhook_url="https://hooks.slack.com/services/T/B/x"),
    )
    assert has_slack_webhook()


def test_post_slack_noop_without_url(no_slack_config):
    assert not post_slack_message("hello")


@patch("shorts_bot.integrations.slack.urllib.request.urlopen")
def test_post_slack_sends_payload(mock_urlopen, monkeypatch):
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.__enter__ = MagicMock(return_value=mock_resp)
    mock_resp.__exit__ = MagicMock(return_value=False)
    mock_urlopen.return_value = mock_resp

    patch_slack_settings(
        monkeypatch,
        slack_webhook_url="https://hooks.slack.com/services/T/B/x",
        slack_channel_email=None,
        gmail_smtp_user=None,
        gmail_smtp_app_password=None,
        slack_post_mode="auto",
        slack_notify_enabled=True,
    )
    ok = post_slack_message("pipeline ok", event="daily")
    assert ok
    req = mock_urlopen.call_args[0][0]
    body = json.loads(req.data.decode())
    assert "pipeline ok" in body["text"]
    assert "[daily]" in body["text"]


def test_slack_status_api():
    r = TestClient(app).get("/api/slack/status")
    assert r.status_code == 200
    data = r.json()
    assert "webhook_configured" in data
    assert "cursor_app" in data
    assert data["checklist"] == "data/SLACK_SETUP_CHECKLIST.md"


def test_has_slack_bot_detects_token(monkeypatch):
    monkeypatch.setattr(
        "shorts_bot.integrations.slack.settings",
        Settings(
            slack_bot_token="xoxb-test-token",
            slack_channel_id="C0123456789",
        ),
    )
    assert has_slack_bot()


@patch("shorts_bot.integrations.slack._post_via_bot_token", return_value=(True, ""))
def test_post_slack_prefers_bot(mock_bot, monkeypatch):
    patch_slack_settings(
        monkeypatch,
        slack_bot_token="xoxb-test",
        slack_channel_id="C0123456789",
        slack_channel_email=None,
        gmail_smtp_user=None,
        gmail_smtp_app_password=None,
        slack_post_mode="auto",
        slack_notify_enabled=True,
    )
    assert post_slack_message("hello")
    mock_bot.assert_called_once()


def test_checklist_includes_slack(monkeypatch):
    monkeypatch.setattr(
        "shorts_bot.integrations.slack.settings",
        Settings(slack_webhook_url="https://hooks.slack.com/services/T/B/x"),
    )
    r = TestClient(app).get("/api/checklist")
    ids = {i["id"] for i in r.json()["items"]}
    assert "slack_cursor" in ids
    assert "slack_bot" in ids


@patch("shorts_bot.integrations.slack.notify_automation_alert", return_value=True)
def test_record_automation_alert_calls_slack(mock_notify, monkeypatch, tmp_path):
    monkeypatch.setattr("shorts_bot.config.settings", Settings(data_dir=tmp_path))
    record_automation_alert("auto_daily", "render failed", detail="timeout")
    mock_notify.assert_called_once_with("auto_daily", "render failed", detail="timeout")


def test_notify_automation_alert_includes_steering_hint(monkeypatch):
    monkeypatch.setattr(
        "shorts_bot.integrations.slack.settings",
        Settings(
            slack_webhook_url="https://hooks.slack.com/services/T/B/x",
            slack_notify_enabled=True,
        ),
    )
    with patch("shorts_bot.integrations.slack.post_slack_message", return_value=True) as mock_post:
        notify_automation_alert("test", "hello", detail="detail")
        text = mock_post.call_args[0][0]
        assert "@cursor" in text


def test_slack_setup_status_shape():
    st = slack_setup_status()
    assert st["channel_suggestion"] == "peripheral-ops"
    assert st["bot_display_name"] == "AlphaBeta001"
    assert "steps" in st
    assert len(st["steps"]) >= 5


def test_slack_test_api_missing_webhook(no_slack_config):
    r = TestClient(app).post("/api/slack/test")
    assert r.status_code == 400


@patch("shorts_bot.integrations.slack.send_test_message", return_value=(True, "OK"))
def test_slack_test_api_ok(mock_send):
    r = TestClient(app).post("/api/slack/test")
    assert r.status_code == 200
    assert r.json()["ok"] is True
