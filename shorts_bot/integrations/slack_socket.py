"""Slack Socket Mode listener — executes [autonomy] commands from the ops channel."""

from __future__ import annotations

import logging
import threading
from typing import Any

from shorts_bot.config import settings

log = logging.getLogger(__name__)

_socket_client: Any = None
_thread: threading.Thread | None = None
_stop = threading.Event()


def socket_mode_available() -> bool:
    from shorts_bot.integrations.slack_autonomy import _socket_ready

    return bool(settings.slack_autonomy_enabled) and _socket_ready()


def _handle_events_api(payload: dict[str, Any]) -> None:
    from shorts_bot.integrations.slack import post_slack_thread
    from shorts_bot.integrations.slack_autonomy import get_bot_user_id, handle_slack_event

    event = payload.get("event") or {}
    if event.get("type") not in ("message", "app_mention"):
        return

    reply = handle_slack_event(event, bot_user_id=get_bot_user_id())
    if not reply:
        return

    ts = event.get("thread_ts") or event.get("ts")
    post_slack_thread(f"```\n{reply[:3500]}\n```", thread_ts=ts)


def _socket_listener_main() -> None:
    global _socket_client

    try:
        from slack_sdk import WebClient
        from slack_sdk.socket_mode import SocketModeClient
        from slack_sdk.socket_mode.request import SocketModeRequest
        from slack_sdk.socket_mode.response import SocketModeResponse
    except ImportError:
        log.warning("slack-sdk not installed — pip install slack-sdk for autonomy bus")
        return

    from shorts_bot.integrations.slack import fetch_bot_user_id
    from shorts_bot.integrations.slack_autonomy import remember_bot_user_id

    bot_token = (settings.slack_bot_token or "").strip()
    app_token = (settings.slack_app_token or "").strip()

    uid = fetch_bot_user_id()
    if uid:
        remember_bot_user_id(uid)
        log.info("Slack autonomy bot user: %s", uid)

    web_client = WebClient(token=bot_token)
    _socket_client = SocketModeClient(app_token=app_token, web_client=web_client)

    def process(client: SocketModeClient, req: SocketModeRequest) -> None:
        if req.type == "events_api":
            try:
                _handle_events_api(req.payload)
            except Exception:  # noqa: BLE001
                log.exception("Slack events_api handler failed")
        client.send_socket_mode_response(SocketModeResponse(envelope_id=req.envelope_id))

    _socket_client.socket_mode_request_listeners.append(process)

    log.info(
        "Slack autonomy socket connecting — #%s [autonomy] self-talk bus",
        settings.slack_channel_name,
    )
    try:
        _socket_client.connect()
    except Exception as exc:  # noqa: BLE001
        if not _stop.is_set():
            log.warning("Slack socket mode stopped: %s", exc)
    finally:
        try:
            if _socket_client:
                _socket_client.close()
        except Exception:  # noqa: BLE001
            pass
        _socket_client = None


def start_slack_socket_listener() -> bool:
    """Start Socket Mode in a daemon thread (idempotent)."""
    global _thread
    if not socket_mode_available():
        return False
    if _thread and _thread.is_alive():
        return True
    _stop.clear()
    _thread = threading.Thread(target=_socket_listener_main, name="slack-socket", daemon=True)
    _thread.start()
    return True


def stop_slack_socket_listener() -> None:
    """Signal shutdown and close the socket client."""
    global _thread, _socket_client
    _stop.set()
    client = _socket_client
    if client is not None:
        try:
            client.close()
        except Exception:  # noqa: BLE001
            pass
    if _thread:
        _thread.join(timeout=5)
        _thread = None


def listener_running() -> bool:
    return _thread is not None and _thread.is_alive()
