"""Post to Slack via channel inbound email — no bot token or webhook."""

from __future__ import annotations

import logging
import re
from typing import Any

from shorts_bot.config import settings
from shorts_bot.integrations.gmail_send import has_gmail_smtp, send_gmail_email

log = logging.getLogger(__name__)


def has_slack_email() -> bool:
    addr = (settings.slack_channel_email or "").strip().lower()
    if "@" not in addr or ".slack.com" not in addr:
        return False
    if "your" in addr or "placeholder" in addr:
        return False
    return has_gmail_smtp()


def _slack_email_address() -> str:
    return (settings.slack_channel_email or "").strip()


def slack_email_status() -> dict[str, Any]:
    addr = _slack_email_address()
    return {
        "configured": has_slack_email(),
        "channel_email_set": "@" in addr and ".slack.com" in addr.lower(),
        "gmail_smtp_set": has_gmail_smtp(),
        "from": (settings.gmail_smtp_user or "").strip() or None,
        "to": addr or None,
        "mode": "outbound_only",
        "doc": "docs/FOR_OWNER_SLACK_EMAIL.md",
        "note": "Shows as email in Slack (from your Gmail). Alerts yes — two-way agent chat no.",
    }


def _subject_for(event: str | None, text: str) -> str:
    brand = "Peripheral"
    first_line = text.strip().split("\n", 1)[0][:72]
    if event:
        return f"[{brand}][{event}] {first_line}"
    return f"[{brand}] {first_line}"


def _plain_body(text: str) -> str:
    """Slack email renders plain text; strip Slack mrkdwn markers lightly."""
    out = text
    out = re.sub(r"\*([^*]+)\*", r"\1", out)
    out = re.sub(r"_([^_]+)_", r"\1", out)
    return out.strip()


def post_slack_via_email(
    text: str,
    *,
    event: str | None = None,
) -> bool:
    """Email the ops channel — appears in Slack as an inbound email message."""
    if not settings.slack_notify_enabled or not has_slack_email():
        return False

    body = _plain_body(text)
    subject = _subject_for(event, body)
    footer = (
        f"\n\n—\n#{settings.slack_channel_name} via Gmail → Slack email\n"
        "(Option A: no bot token)"
    )
    ok, err = send_gmail_email(
        to=_slack_email_address(),
        subject=subject,
        body=body + footer,
    )
    if not ok:
        log.warning("Slack email post failed: %s", err)
    return ok
