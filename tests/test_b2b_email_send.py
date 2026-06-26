# Tests for B2B outreach email (dedicated inbox)

import json
from datetime import datetime, timezone
from pathlib import Path

from shorts_bot.b2b import email_send


def _settings(**kwargs):
    defaults = {
        "b2b_email_from_name": "Kim",
        "b2b_smtp_user": "outreach@example.com",
        "b2b_smtp_app_password": "abcdefghijklmnop",
        "b2b_smtp_host": "smtp.gmail.com",
        "b2b_smtp_port": 587,
        "b2b_test_email": "owner@example.com",
        "b2b_email_enabled": False,
        "b2b_email_daily_limit": 10,
        "data_dir": Path("data"),
    }
    defaults.update(kwargs)
    return type("S", (), defaults)()


def test_from_header_uses_outreach_inbox(monkeypatch):
    monkeypatch.setattr("shorts_bot.b2b.email_send.settings", _settings())
    assert "Kim" in email_send.from_header()
    assert "outreach@example.com" in email_send.from_header()


def test_smtp_configured_requires_b2b_credentials(monkeypatch):
    monkeypatch.setattr(
        "shorts_bot.b2b.email_send.settings",
        _settings(b2b_smtp_user=None, b2b_smtp_app_password=None),
    )
    assert not email_send.smtp_configured()


def test_can_send_more_disabled_by_default(monkeypatch):
    monkeypatch.setattr("shorts_bot.b2b.email_send.settings", _settings())
    ok, msg = email_send.can_send_more()
    assert not ok
    assert "disabled" in msg.lower()


def test_can_send_more_respects_daily_limit(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "shorts_bot.b2b.email_send.settings",
        _settings(b2b_email_enabled=True, data_dir=tmp_path),
    )
    log = tmp_path / "b2b" / "send_log.jsonl"
    log.parent.mkdir(parents=True)
    today = datetime.now(timezone.utc).isoformat()
    log.write_text(
        "\n".join(json.dumps({"at": today, "ok": True}) for _ in range(2)) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "shorts_bot.b2b.email_send.settings",
        _settings(b2b_email_enabled=True, b2b_email_daily_limit=2, data_dir=tmp_path),
    )
    ok, msg = email_send.can_send_more()
    assert not ok
    assert "limit" in msg.lower()


def test_send_uses_b2b_smtp_not_ops_gmail(monkeypatch):
    monkeypatch.setattr(
        "shorts_bot.b2b.email_send.settings",
        _settings(b2b_email_enabled=True),
    )
    calls: list[dict] = []

    def fake_send(**kwargs):
        calls.append(kwargs)
        return True, ""

    monkeypatch.setattr(email_send, "send_smtp_email", fake_send)
    monkeypatch.setattr(email_send, "log_send", lambda **kwargs: None)

    ok, _ = email_send.send_business_email(
        to="founder@startup.com",
        subject="Quick question",
        body="Hey — saw your launch.",
        company="Startup",
    )
    assert ok
    assert calls[0]["smtp_user"] == "outreach@example.com"
    assert calls[0]["to"] == "founder@startup.com"


def test_send_invalid_recipient(monkeypatch):
    monkeypatch.setattr(
        "shorts_bot.b2b.email_send.settings",
        _settings(b2b_email_enabled=True),
    )
    ok, msg = email_send.send_business_email(to="not-an-email", subject="Hi", body="Hi")
    assert not ok
    assert "invalid" in msg.lower()
