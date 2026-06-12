"""Slack — AlphaBeta001 bot token and/or webhook; @cursor is separate."""

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
SLACK_APPS_URL = "https://api.slack.com/apps"


def has_slack_webhook() -> bool:
    url = (settings.slack_webhook_url or "").strip()
    if not url or "hooks.slack.com" not in url:
        return False
    lower = url.lower()
    return "your-webhook" not in lower and "placeholder" not in lower


def has_slack_bot() -> bool:
    token = (settings.slack_bot_token or "").strip()
    channel = (settings.slack_channel_id or "").strip()
    if not token.startswith("xoxb-") or not channel.startswith("C"):
        return False
    return "your" not in token.lower() and "placeholder" not in token.lower()


def slack_can_post() -> bool:
    from shorts_bot.integrations.slack_email import has_slack_email

    return has_slack_bot() or has_slack_webhook() or has_slack_email()


def slack_cursor_linked() -> bool:
    return bool(settings.slack_cursor_linked)


def slack_setup_steps() -> list[dict[str, Any]]:
    """Ordered checklist for web UI and owner walkthrough."""
    ch = settings.slack_channel_name
    webhook = has_slack_webhook()
    bot = has_slack_bot()
    cursor = slack_cursor_linked()
    from shorts_bot.integrations.slack_email import has_slack_email

    email = has_slack_email()
    return [
        {
            "id": "channel_email",
            "phase": "email",
            "label": "Option A: Gmail → channel email (no bot token)",
            "done": email,
            "url": None,
            "detail": (
                "#"
                + ch
                + " → Integrations → Email → copy address → "
                "SLACK_CHANNEL_EMAIL + Gmail app password"
            ),
        },
        {
            "id": "bot_app",
            "phase": "bot",
            "label": "Create AlphaBeta001 Slack app (your bot)",
            "done": bot,
            "url": SLACK_APPS_URL,
            "detail": "api.slack.com → Create app → chat:write → Install → add to #" + ch,
        },
        {
            "id": "bot_secrets",
            "phase": "bot",
            "label": "Secrets: SLACK_BOT_TOKEN + SLACK_CHANNEL_ID",
            "done": bot,
            "url": None,
            "detail": "See docs/FOR_OWNER_SLACK_BOT.md — then bash scripts/install.sh",
        },
        {
            "id": "cursor_install",
            "phase": "@cursor",
            "label": "Install Cursor app in Slack (optional — remote agents)",
            "done": cursor,
            "url": CURSOR_INTEGRATIONS_URL,
            "detail": "Separate from AlphaBeta001 bot. DM Cursor → @cursor help → Link Account.",
        },
        {
            "id": "cursor_link",
            "phase": "@cursor",
            "label": "Link Account in DM with Cursor (not just add to channel)",
            "done": cursor,
            "url": None,
            "detail": "Apps → Cursor → @cursor help → Link Account. Set SLACK_CURSOR_LINKED=true after.",
        },
        {
            "id": "webhook_create",
            "phase": "webhook",
            "label": f"Incoming Webhook (optional if bot token set)",
            "done": webhook,
            "url": "https://api.slack.com/messaging/webhooks",
            "detail": "Only needed if you skip custom bot app.",
        },
        {
            "id": "socket_mode",
            "phase": "autonomy",
            "label": "Socket Mode + SLACK_APP_TOKEN ([autonomy] self-talk bus)",
            "done": slack_autonomy_status()["socket_ready"],
            "url": SLACK_APPS_URL,
            "detail": "Enable Socket Mode → App-Level Token xapp-… → subscribe message.channels + app_mention",
        },
        {
            "id": "webhook_test",
            "phase": "bot",
            "label": "Test post (web Slack tab or integrations test)",
            "done": bot or webhook or email,
            "url": None,
            "detail": "python3 -m shorts_bot.integrations test",
        },
        {
            "id": "mcp_connect",
            "phase": "mcp",
            "label": "Slack MCP in Cursor Desktop (optional)",
            "done": False,
            "url": SLACK_MCP_MARKETPLACE_URL,
            "detail": "Agents post progress while grinding.",
        },
        {
            "id": "automations",
            "phase": "automations",
            "label": "Cursor automations (subscriber count, daily post)",
            "done": False,
            "url": CURSOR_AUTOMATIONS_URL,
            "detail": "Owner-configured in dashboard.",
        },
    ]


def slack_setup_status() -> dict[str, Any]:
    webhook = has_slack_webhook()
    bot = has_slack_bot()
    cursor = slack_cursor_linked()
    steps = slack_setup_steps()
    done_count = sum(1 for s in steps if s["done"])
    from shorts_bot.integrations.slack_email import has_slack_email, slack_email_status

    email = has_slack_email()
    mode = (
        "bot"
        if bot
        else ("webhook" if webhook else ("email" if email else "none"))
    )
    return {
        "mode": mode,
        "bot_configured": bot,
        "bot_display_name": settings.slack_bot_display_name,
        "webhook_configured": webhook,
        "webhook_enabled": settings.slack_notify_enabled and slack_can_post(),
        "cursor_linked": cursor,
        "cursor_app": {
            "configured": cursor,
            "note": "@cursor is NOT the AlphaBeta001 bot — Link Account in DM with Cursor app.",
            "doc": "docs/SLACK_CURSOR_SETUP.md",
            "owner_guide": "docs/FOR_OWNER_SLACK.md",
            "bot_guide": "docs/FOR_OWNER_SLACK_BOT.md",
            "dashboard": CURSOR_INTEGRATIONS_URL,
        },
        "channel_suggestion": settings.slack_channel_name,
        "checklist": "data/SLACK_SETUP_CHECKLIST.md",
        "setup_script": "bash scripts/slack-setup.sh",
        "steps": steps,
        "progress": f"{done_count}/{len(steps)}",
        "ready": bot or webhook or email,
        "email": slack_email_status(),
        "post_mode": (settings.slack_post_mode or "auto").strip().lower(),
        "autonomy": slack_autonomy_status(),
        "test_prompt": (
            f"@cursor agent in proof-codex-ai — reply OK in #{settings.slack_channel_name}. "
            f"(Or wait for {settings.slack_bot_display_name} bot test message.)"
        ),
    }


def _post_via_bot_token(
    text: str,
    *,
    thread_ts: str | None = None,
) -> tuple[bool, str]:
    token = (settings.slack_bot_token or "").strip()
    channel = (settings.slack_channel_id or "").strip()
    body: dict[str, Any] = {"channel": channel, "text": text}
    if thread_ts:
        body["thread_ts"] = thread_ts
    payload = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        "https://slack.com/api/chat.postMessage",
        data=payload,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read().decode())
        if body.get("ok"):
            return True, ""
        return False, str(body.get("error", "unknown_error"))
    except urllib.error.HTTPError as exc:
        return False, f"HTTP {exc.code}"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def _post_via_webhook(text: str, *, blocks: list[dict[str, Any]] | None = None) -> bool:
    url = (settings.slack_webhook_url or "").strip()
    payload: dict[str, Any] = {"text": text}
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


def post_slack_thread(text: str, *, thread_ts: str | None = None) -> bool:
    """Reply in a thread (or start a thread when thread_ts is the parent message ts)."""
    if not settings.slack_notify_enabled or not has_slack_bot():
        return False
    ok, err = _post_via_bot_token(text, thread_ts=thread_ts)
    if not ok:
        log.warning("Slack thread post failed: %s", err)
    return ok


def fetch_bot_user_id() -> str | None:
    """auth.test — cache bot user id for autonomy self-talk detection."""
    token = (settings.slack_bot_token or "").strip()
    if not token.startswith("xoxb-"):
        return None
    req = urllib.request.Request(
        "https://slack.com/api/auth.test",
        data=b"",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read().decode())
        if body.get("ok"):
            return str(body.get("user_id") or "") or None
        log.warning("Slack auth.test failed: %s", body.get("error"))
    except Exception as exc:  # noqa: BLE001
        log.warning("Slack auth.test error: %s", exc)
    return None


def slack_autonomy_status() -> dict[str, Any]:
    from shorts_bot.integrations.slack_autonomy import autonomy_enabled, _socket_ready

    app = (settings.slack_app_token or "").strip()
    return {
        "enabled": bool(settings.slack_autonomy_enabled),
        "socket_ready": _socket_ready(),
        "active": autonomy_enabled(),
        "app_token_set": app.startswith("xapp-"),
        "owner_commands": bool(settings.slack_autonomy_owner_commands),
        "prefix": "[autonomy]",
        "doc": "docs/SLACK_AUTONOMY.md",
    }


def _post_mode() -> str:
    return (settings.slack_post_mode or "auto").strip().lower()


def post_slack_message(
    text: str,
    *,
    blocks: list[dict[str, Any]] | None = None,
    event: str | None = None,
) -> bool:
    """Post via bot token, webhook, or Gmail → Slack channel email."""
    from shorts_bot.integrations.slack_email import has_slack_email, post_slack_via_email

    if not settings.slack_notify_enabled:
        return False

    prefix = f"*[{event}]* " if event else ""
    full = f"{prefix}{text}"
    mode = _post_mode()

    if mode == "email":
        return post_slack_via_email(full, event=event)

    if mode != "email" and has_slack_bot():
        ok, err = _post_via_bot_token(full)
        if ok:
            return True
        log.warning("Slack bot post failed: %s — trying fallbacks", err)

    if mode != "email" and has_slack_webhook():
        if _post_via_webhook(full, blocks=blocks):
            return True

    if mode in ("auto", "email") and has_slack_email():
        return post_slack_via_email(full, event=event)

    return False


def notify_automation_alert(event: str, message: str, *, detail: str = "") -> bool:
    lines = [message]
    if detail:
        lines.append(f"```{detail[:800]}```")
    from shorts_bot.integrations.slack_email import has_slack_email

    if not has_slack_bot() and not has_slack_email():
        lines.append("_Remote agents: `@cursor agent …` in Slack (needs Link Account in DM)._")
    elif has_slack_email() and not has_slack_bot():
        lines.append("_Posted via Gmail → Slack email. Reply in channel or `@cursor` for steering._")
    return post_slack_message("\n".join(lines), event=event)


def send_test_message() -> tuple[bool, str]:
    name = settings.slack_bot_display_name
    body = (
        f"👁 *{name}* online — Peripheral ops bot.\n"
        "Pipeline alerts and milestones post here.\n"
        "_First subscriber logged. don't blink._"
    )
    from shorts_bot.integrations.slack_email import has_slack_email

    if not slack_can_post():
        return (
            False,
            "Option A: SLACK_CHANNEL_EMAIL + GMAIL_SMTP_* (docs/FOR_OWNER_SLACK_EMAIL.md). "
            "Or SLACK_BOT_TOKEN + SLACK_CHANNEL_ID, or SLACK_WEBHOOK_URL",
        )
    ok = post_slack_message(body, event="setup")
    if ok:
        if has_slack_bot():
            via = name
        elif has_slack_email() and _post_mode() in ("auto", "email"):
            via = f"Gmail → #{settings.slack_channel_name} email"
        else:
            via = "webhook"
        return True, f"Posted as {via}"
    return False, (
        "Post failed — check Gmail app password or Slack channel email. "
        "If Gmail Sent shows OK but Slack is empty: delete & regenerate channel "
        "email in Slack Integrations, update SLACK_CHANNEL_EMAIL, re-run install.sh"
    )
