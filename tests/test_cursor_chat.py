"""Tests for Cursor chat automation."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from shorts_bot.desktop_hub.cursor_chat import (
    CursorChatError,
    _coords_from_schedule,
    resolve_cursor_coords,
    send_cursor_message,
)


def test_coords_from_schedule(tmp_path, monkeypatch):
    sched = tmp_path / "schedule.json"
    sched.write_text(
        json.dumps(
            {
                "daily_prelaunch": {
                    "focus_x": 100,
                    "focus_y": 200,
                    "submit_x": 300,
                    "submit_y": 400,
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr("shorts_bot.desktop_hub.cursor_chat.SCHEDULE_JSON", sched)
    assert _coords_from_schedule() == (100, 200, 300, 400)


def test_resolve_cursor_coords_uses_calibrated_schedule(tmp_path, monkeypatch):
    sched = tmp_path / "schedule.json"
    sched.write_text(
        json.dumps(
            {
                "daily_prelaunch": {
                    "focus_x": 100,
                    "focus_y": 200,
                    "submit_x": 300,
                    "submit_y": 400,
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr("shorts_bot.desktop_hub.cursor_chat.SCHEDULE_JSON", sched)
    assert resolve_cursor_coords() == (100, 200, 300, 400)


def test_resolve_cursor_coords_rejects_zero(monkeypatch):
    monkeypatch.setattr("shorts_bot.desktop_hub.cursor_chat._coords_from_schedule", lambda: None)
    with patch(
        "shorts_bot.desktop_hub.cursor_chat.subprocess.run",
        side_effect=[
            MagicMock(stdout="/mnt/c/tmp/coords.ps1\n", returncode=0),
            MagicMock(stdout="0 0 0 0\n", stderr="", returncode=0),
        ],
    ), patch("shorts_bot.desktop_hub.cursor_chat._windows_powershell", return_value=MagicMock(is_file=lambda: True)):
        fake_root = MagicMock()
        fake_root.__truediv__ = lambda s, x: MagicMock(is_file=lambda: True)
        with pytest.raises(CursorChatError, match="coords are 0"):
            resolve_cursor_coords(repo_root=fake_root)


def test_send_cursor_message_hotkey_path_types_full_text(monkeypatch):
    client = MagicMock()
    client.ping.return_value = "alive"
    monkeypatch.setattr("shorts_bot.desktop_hub.cursor_chat._coords_from_schedule", lambda: None)
    monkeypatch.setattr("shorts_bot.desktop_hub.cursor_chat._load_helper_env", lambda: None)
    monkeypatch.setattr("shorts_bot.desktop_hub.cursor_chat.DesktopHubClient", lambda: client)
    monkeypatch.setattr("shorts_bot.desktop_hub.cursor_chat.time.sleep", lambda _: None)

    coords = send_cursor_message("Hub CEO: full message with spaces")
    assert coords == (-1, -1, -1, -1)
    client.hotkey.assert_called_once_with("ctrl", "l")
    client.type_text.assert_called_once_with("Hub CEO: full message with spaces")
    client.press.assert_called_once_with("enter")


def test_send_cursor_message_calibrated_click_path(monkeypatch):
    client = MagicMock()
    client.ping.return_value = "alive"
    monkeypatch.setattr(
        "shorts_bot.desktop_hub.cursor_chat._coords_from_schedule",
        lambda: (10, 20, 30, 40),
    )
    monkeypatch.setattr("shorts_bot.desktop_hub.cursor_chat._focus_cursor_window", lambda **_: None)
    monkeypatch.setattr("shorts_bot.desktop_hub.cursor_chat._load_helper_env", lambda: None)
    monkeypatch.setattr("shorts_bot.desktop_hub.cursor_chat.DesktopHubClient", lambda: client)
    monkeypatch.setattr("shorts_bot.desktop_hub.cursor_chat.time.sleep", lambda _: None)

    coords = send_cursor_message("calibrated path")
    assert coords == (10, 20, 30, 40)
    client.click.assert_any_call(10, 20)
    client.click.assert_any_call(30, 40)
    client.type_text.assert_called_once_with("calibrated path")


def test_cursor_send_via_hub_uses_msg_b64_and_run_remote(monkeypatch):
    from shorts_bot.desktop_hub.cursor_chat import cursor_send_via_hub

    calls: list[list[str]] = []

    def fake_run_remote(cmd: list[str]) -> int:
        calls.append(cmd)
        return 0

    monkeypatch.setattr("shorts_bot.hub_remote.run_remote", fake_run_remote)
    assert cursor_send_via_hub("Hub CEO: full message") == 0
    assert len(calls) == 1
    assert calls[0][0:3] == ["python3", "scripts/hub_cursor_send.py", "--msg-b64"]
    import base64

    assert base64.b64decode(calls[0][3]).decode("utf-8") == "Hub CEO: full message"
