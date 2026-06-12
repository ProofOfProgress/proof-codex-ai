from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from shorts_bot.automation.alerts import record_automation_alert
from shorts_bot.config import Settings
from shorts_bot.integrations.slack import (
    has_slack_webhook,
    notify_automation_alert,
    post_slack_message,
    slack_setup_status,
)
from shorts_bot.web.app import app


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


def test_post_slack_noop_without_url(monkeypatch):
    monkeypatch.setattr(
        "shorts_bot.integrations.slack.settings",
        Settings(slack_webhook_url=None, slack_notify_enabled=True),
    )
    assert not post_slack_message("hello")


@patch("shorts_bot.integrations.slack.urllib.request.urlopen")
def test_post_slack_sends_payload(mock_urlopen, monkeypatch):
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.__enter__ = MagicMock(return_value=mock_resp)
    mock_resp.__exit__ = MagicMock(return_value=False)
    mock_urlopen.return_value = mock_resp

    monkeypatch.setattr(
        "shorts_bot.integrations.slack.settings",
        Settings(
            slack_webhook_url="https://hooks.slack.com/services/T/B/x",
            slack_notify_enabled=True,
        ),
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


def test_checklist_includes_slack(monkeypatch):
    monkeypatch.setattr(
        "shorts_bot.integrations.slack.settings",
        Settings(slack_webhook_url="https://hooks.slack.com/services/T/B/x"),
    )
    r = TestClient(app).get("/api/checklist")
    ids = {i["id"] for i in r.json()["items"]}
    assert "slack_cursor" in ids
    assert "slack_webhook" in ids


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
    assert st["channel_suggestion"] == "dont-blink-ops"
