"""Slack incoming webhook — pipeline alerts + setup status for @cursor."""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from typing import Any

from shorts_bot.config import settings

log = logging.getLogger(__name__)

CURSOR_INTEGRATIONS_URL = "https://cursor.com/dashboard?tab=integrations"
CURSOR_AUTOMATIONS_URL = "https://cursor.com/automations"
SLACK_MCP_MARKETPLACE_URL = "https://cursor.com/marketplace/slack"


def has_slack_webhook() -> bool:
    url = (settings.slack_webhook_url or "").strip()
    if not url or "hooks.slack.com" not in url:
        return False
    lower = url.lower()
    return "your-webhook" not in lower and "placeholder" not in lower


def slack_cursor_linked() -> bool:
    return bool(settings.slack_cursor_linked)


def slack_setup_steps() -> list[dict[str, Any]]:
    """Ordered checklist for web UI and owner walkthrough."""
    ch = settings.slack_channel_name
    webhook = has_slack_webhook()
    cursor = slack_cursor_linked()
    return [
        {
            "id": "cursor_install",
            "phase": "@cursor",
            "label": "Install Cursor app in Slack",
            "done": cursor,
            "url": CURSOR_INTEGRATIONS_URL,
            "detail": "Dashboard → Integrations → Slack → Connect. Connect GitHub repo proof-codex-ai.",
        },
        {
            "id": "cursor_channel",
            "phase": "@cursor",
            "label": f"Create #{ch} and /invite @cursor",
            "done": cursor,
            "url": None,
            "detail": "Public channel required. Then type: @cursor help → Link Account (OAuth).",
        },
        {
            "id": "cursor_defaults",
            "phase": "@cursor",
            "label": "@cursor settings → default repo proof-codex-ai",
            "done": cursor,
            "url": None,
            "detail": "Optional routing keywords: shorts, peripheral, dont-blink.",
        },
        {
            "id": "cursor_test",
            "phase": "@cursor",
            "label": "Test @cursor in Slack",
            "done": cursor,
            "url": None,
            "detail": "@cursor agent in proof-codex-ai, read docs/SLACK_CURSOR_SETUP.md and reply OK",
        },
        {
            "id": "webhook_create",
            "phase": "webhook",
            "label": f"Incoming Webhook → #{ch}",
            "done": webhook,
            "url": "https://api.slack.com/messaging/webhooks",
            "detail": "Slack → Apps → Incoming Webhooks → Add. Copy the https://hooks.slack.com/... URL.",
        },
        {
            "id": "webhook_secret",
            "phase": "webhook",
            "label": "Add SLACK_WEBHOOK_URL to Cursor Secrets",
            "done": webhook,
            "url": CURSOR_INTEGRATIONS_URL,
            "detail": "Then run: bash scripts/install.sh",
        },
        {
            "id": "webhook_test",
            "phase": "webhook",
            "label": "Test webhook (button below or CLI)",
            "done": webhook,
            "url": None,
            "detail": "python3 -m shorts_bot.integrations test",
        },
        {
            "id": "mcp_connect",
            "phase": "mcp",
            "label": "Slack MCP in Cursor Desktop (optional)",
            "done": False,
            "url": SLACK_MCP_MARKETPLACE_URL,
            "detail": "Lets agents post progress while grinding. Enable for Cloud Agents in dashboard too.",
        },
        {
            "id": "automations",
            "phase": "automations",
            "label": "Cursor automations (subscriber count, daily post)",
            "done": False,
            "url": CURSOR_AUTOMATIONS_URL,
            "detail": "Owner-configured — subscriber milestones + daily grind prompts.",
        },
    ]


def slack_setup_status() -> dict[str, Any]:
    webhook = has_slack_webhook()
    cursor = slack_cursor_linked()
    steps = slack_setup_steps()
    done_count = sum(1 for s in steps if s["done"])
    return {
        "webhook_configured": webhook,
        "webhook_enabled": settings.slack_notify_enabled and webhook,
        "cursor_linked": cursor,
        "cursor_app": {
            "configured": cursor,
            "note": "Set SLACK_CURSOR_LINKED=true in Cursor Secrets after @cursor Link Account.",
            "doc": "docs/SLACK_CURSOR_SETUP.md",
            "owner_guide": "docs/FOR_OWNER_SLACK.md",
            "dashboard": CURSOR_INTEGRATIONS_URL,
        },
        "channel_suggestion": settings.slack_channel_name,
        "checklist": "data/SLACK_SETUP_CHECKLIST.md",
        "setup_script": "bash scripts/slack-setup.sh",
        "steps": steps,
        "progress": f"{done_count}/{len(steps)}",
        "ready": webhook and cursor,
        "test_prompt": (
            f"@cursor agent in proof-codex-ai — Peripheral Slack is live. "
            f"Read docs/SLACK_CURSOR_SETUP.md and reply OK in #{settings.slack_channel_name}."
        ),
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
    """Ping webhook — for CLI and web test button."""
    if not has_slack_webhook():
        return False, "SLACK_WEBHOOK_URL missing — add Incoming Webhook URL to Cursor Secrets"
    ok = post_slack_message(
        "🎉 *Peripheral* bot connected to Slack.\n"
        "Pipeline alerts will post here. First subscriber energy — let's go.\n"
        "Start agents: `@cursor agent take 1h on proof-codex-ai — …`",
        event="setup",
    )
    if ok:
        return True, f"Posted test message to #{settings.slack_channel_name}"
    return False, "Webhook request failed — regenerate URL in Slack app settings"
