"""Slack autonomy bus — bot posts [autonomy] commands and executes them from Socket Mode."""

from __future__ import annotations

import logging
import re
from collections import deque
from threading import Lock
from typing import Any

from shorts_bot.config import settings

log = logging.getLogger(__name__)

AUTONOMY_PREFIX = "[autonomy]"
_MAX_DEDUPE = 200
_seen_events: deque[str] = deque(maxlen=_MAX_DEDUPE)
_dedupe_lock = Lock()

_bot_user_id: str | None = None


def autonomy_enabled() -> bool:
    return bool(settings.slack_autonomy_enabled) and _socket_ready()


def _socket_ready() -> bool:
    app = (settings.slack_app_token or "").strip()
    bot = (settings.slack_bot_token or "").strip()
    ch = (settings.slack_channel_id or "").strip()
    return app.startswith("xapp-") and bot.startswith("xoxb-") and ch.startswith("C")


def remember_bot_user_id(user_id: str) -> None:
    global _bot_user_id
    _bot_user_id = user_id


def get_bot_user_id() -> str | None:
    return _bot_user_id


def _event_seen(event_id: str) -> bool:
    with _dedupe_lock:
        if event_id in _seen_events:
            return True
        _seen_events.append(event_id)
        return False


def strip_autonomy_prefix(text: str) -> str | None:
    t = (text or "").strip()
    if not t:
        return None
    lower = t.lower()
    if lower.startswith(AUTONOMY_PREFIX.lower()):
        body = t[len(AUTONOMY_PREFIX) :].strip()
        return body or None
    return None


def _strip_bot_mention(text: str) -> str:
    """Remove <@U123> leading mention."""
    return re.sub(r"^<@[A-Z0-9]+>\s*", "", (text or "").strip())


def parse_slack_command(event: dict[str, Any], *, bot_user_id: str | None = None) -> str | None:
    """
    Return command text to run, or None if this event should be ignored.
    Self-talk: bot's own messages with [autonomy] prefix are executed.
    """
    if not autonomy_enabled():
        return None

    channel = (settings.slack_channel_id or "").strip()
    if event.get("channel") != channel:
        return None

    subtype = event.get("subtype")
    if subtype in ("message_changed", "message_deleted", "channel_join", "channel_leave"):
        return None

    event_id = str(event.get("client_msg_id") or event.get("ts") or "")
    if event_id and _event_seen(event_id):
        return None

    text = _strip_bot_mention(event.get("text", ""))
    cmd = strip_autonomy_prefix(text)
    if cmd:
        return cmd

    if event.get("type") == "app_mention" and text:
        return text

    if settings.slack_autonomy_owner_commands and subtype != "bot_message":
        user = event.get("user")
        if user and user != bot_user_id and text:
            return text

    return None


def execute_slack_command(command: str) -> str:
    """Run through the same router as web chat."""
    from shorts_bot.services.ops import BotOperations

    try:
        return BotOperations().chat(command)
    except Exception as exc:  # noqa: BLE001
        log.exception("Slack autonomy command failed")
        return f"Error: {exc}"


def handle_slack_event(event: dict[str, Any], *, bot_user_id: str | None = None) -> str | None:
    """
    Process one Slack message event. Returns reply text if handled.
    """
    bid = bot_user_id or get_bot_user_id()
    command = parse_slack_command(event, bot_user_id=bid)
    if not command:
        return None

    who = "self" if event.get("bot_id") or event.get("user") == bid else "channel"
    log.info("Slack autonomy [%s]: %s", who, command[:80])
    reply = execute_slack_command(command)
    return reply[:3900] if reply else "Done."


def post_autonomy_command(
    command: str,
    *,
    note: str = "",
    thread_ts: str | None = None,
) -> tuple[bool, str]:
    """
    Post [autonomy] command to Slack — Socket Mode listener executes it (self-talk bus).
    If socket is off but autonomy enabled, runs immediately and still posts result.
    """
    from shorts_bot.integrations.slack import has_slack_bot, post_slack_message, post_slack_thread

    cmd = command.strip()
    if not cmd:
        return False, "Empty command"

    lines = [f"{AUTONOMY_PREFIX} {cmd}"]
    if note:
        lines.append(f"_{note}_")

    text = "\n".join(lines)
    if not has_slack_bot():
        if autonomy_enabled():
            reply = execute_slack_command(cmd)
            return True, reply
        return False, "SLACK_BOT_TOKEN required for autonomy bus"

    ok = post_slack_thread(text, thread_ts=thread_ts) if thread_ts else post_slack_message(text)
    if not ok:
        return False, "Failed to post to Slack"

    if not _socket_ready():
        reply = execute_slack_command(cmd)
        post_slack_thread(f"```\n{reply[:3500]}\n```", thread_ts=thread_ts)
        return True, "Posted + ran locally (socket mode off)"

    return True, "Posted to autonomy bus — socket listener will execute"
