# Tests for B2B business email send

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from shorts_bot.b2b import email_send


def test_from_header_uses_name_and_address(monkeypatch):
    monkeypatch.setattr(
        "shorts_bot.b2b.email_send.settings",
        type(
            "S",
            (),
            {
                "b2b_email_from_name": "Kim",
                "gmail_smtp_user": "kim@example.com",
                "business_email_user": None,
            },
        )(),
    )
    assert "Kim" in email_send.from_header()
    assert "kim@example.com" in email_send.from_header()


def test_can_send_more_disabled_by_default(monkeypatch):
    monkeypatch.setattr(
        "shorts_bot.b2b.email_send.settings",
        type(
            "S",
            (),
            {
                "b2b_email_enabled": False,
                "b2b_email_daily_limit": 10,
            },
        )(),
    )
    monkeypatch.setattr(email_send, "smtp_configured", lambda: True)
    ok, msg = email_send.can_send_more()
    assert not ok
    assert "disabled" in msg.lower()


def test_can_send_more_respects_daily_limit(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "shorts_bot.b2b.email_send.settings",
        type(
            "S",
            (),
            {
                "b2b_email_enabled": True,
                "b2b_email_daily_limit": 2,
                "data_dir": tmp_path,
            },
        )(),
    )
    monkeypatch.setattr(email_send, "smtp_configured", lambda: True)
    log = tmp_path / "b2b" / "send_log.jsonl"
    log.parent.mkdir(parents=True)
    today = datetime.now(timezone.utc).isoformat()
    log.write_text(
        "\n".join(
            json.dumps({"at": today, "ok": True}) for _ in range(2)
        )
        + "\n",
        encoding="utf-8",
    )
    ok, msg = email_send.can_send_more()
    assert not ok
    assert "limit" in msg.lower()


def test_send_business_email_calls_gmail(monkeypatch):
    monkeypatch.setattr(email_send, "can_send_more", lambda: (True, ""))
    calls: list[dict] = []

    def fake_send(**kwargs):
        calls.append(kwargs)
        return True, ""

    monkeypatch.setattr(email_send, "send_gmail_email", fake_send)
    monkeypatch.setattr(email_send, "log_send", lambda **kwargs: None)

    ok, msg = email_send.send_business_email(
        to="founder@startup.com",
        subject="Quick question",
        body="Hey — saw your launch.",
        company="Startup",
    )
    assert ok
    assert calls[0]["to"] == "founder@startup.com"
    assert "Quick question" in calls[0]["subject"]


def test_send_business_email_invalid_recipient(monkeypatch):
    monkeypatch.setattr(email_send, "can_send_more", lambda: (True, ""))
    ok, msg = email_send.send_business_email(
        to="not-an-email",
        subject="Hi",
        body="Hi",
    )
    assert not ok
    assert "invalid" in msg.lower()
