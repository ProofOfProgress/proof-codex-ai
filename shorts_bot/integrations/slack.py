"""Slack incoming webhook — pipeline alerts to #dont-blink-ops (or any channel)."""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from typing import Any

from shorts_bot.config import settings

log = logging.getLogger(__name__)


def has_slack_webhook() -> bool:
    url = (settings.slack_webhook_url or "").strip()
    if not url or "hooks.slack.com" not in url:
        return False
    lower = url.lower()
    return "your-webhook" not in lower and "placeholder" not in lower


def slack_setup_status() -> dict[str, Any]:
    """Status for web UI / login_status — @cursor OAuth is manual; webhook is env-detectable."""
    webhook = has_slack_webhook()
    return {
        "webhook_configured": webhook,
        "webhook_enabled": settings.slack_notify_enabled and webhook,
        "cursor_app": {
            "configured": False,
            "note": "Install @cursor in Slack + link your Cursor account (OAuth — owner only).",
            "doc": "docs/SLACK_CURSOR_SETUP.md",
            "dashboard": "https://cursor.com/dashboard?tab=integrations",
        },
        "channel_suggestion": settings.slack_channel_name,
        "checklist": "data/SLACK_SETUP_CHECKLIST.md",
    }


def post_slack_message(
    text: str,
    *,
    blocks: list[dict[str, Any]] | None = None,
    event: str | None = None,
) -> bool:
    """
    Post to Slack incoming webhook. Returns True on 200.
    No-op when webhook missing or slack_notify_enabled=false.
    """
    if not settings.slack_notify_enabled or not has_slack_webhook():
        return False

    url = (settings.slack_webhook_url or "").strip()
    prefix = f"*[{event}]* " if event else ""
    payload: dict[str, Any] = {"text": f"{prefix}{text}"}
    if blocks:
        payload["blocks"] = blocks

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return 200 <= resp.status < 300
    except urllib.error.HTTPError as exc:
        log.warning("Slack webhook HTTP %s: %s", exc.code, exc.read()[:200])
        return False
    except Exception as exc:  # noqa: BLE001
        log.warning("Slack webhook failed: %s", exc)
        return False


def notify_automation_alert(event: str, message: str, *, detail: str = "") -> bool:
    """Format pipeline alert for Slack."""
    lines = [message]
    if detail:
        lines.append(f"```{detail[:800]}```")
    lines.append("_Steer from phone: `@cursor agent …` in Slack — see docs/SLACK_CURSOR_SETUP.md_")
    return post_slack_message("\n".join(lines), event=event)


def send_test_message() -> tuple[bool, str]:
    """Ping webhook — for `python3 -m shorts_bot.integrations.slack_cli test`."""
    if not has_slack_webhook():
        return False, "SLACK_WEBHOOK_URL missing or invalid — see docs/SLACK_CURSOR_SETUP.md Part 3"
    ok = post_slack_message(
        "Peripheral bot connected. Pipeline alerts will post here.\n"
        "Start agents from this channel: `@cursor agent take 1h on proof-codex-ai — …`",
        event="setup",
    )
    if ok:
        return True, f"Posted test message to #{settings.slack_channel_name}"
    return False, "Webhook request failed — regenerate URL in Slack app settings"
