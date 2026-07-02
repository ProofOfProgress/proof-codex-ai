"""Tests for Cursor chat automation."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from shorts_bot.desktop_hub.cursor_chat import CursorChatError, resolve_cursor_coords, send_cursor_message


def test_resolve_cursor_coords_uses_calibrated_schedule(tmp_path, monkeypatch):
    sched = tmp_path / "schedule.json"
    sched.write_text(
        '{"daily_prelaunch": {"focus_x": 100, "focus_y": 200, "submit_x": 300, "submit_y": 400}}',
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "shorts_bot.desktop_hub.cursor_chat.load_prelaunch_schedule",
        lambda path=None: __import__(
            "shorts_bot.desktop_hub.prelaunch_trigger", fromlist=["load_prelaunch_schedule"]
        ).load_prelaunch_schedule(sched),
    )
    assert resolve_cursor_coords() == (100, 200, 300, 400)


def test_resolve_cursor_coords_rejects_zero():
    with patch(
        "shorts_bot.desktop_hub.cursor_chat.load_prelaunch_schedule",
        return_value=MagicMock(focus_x=0, focus_y=0, submit_x=0, submit_y=0),
    ), patch(
        "shorts_bot.desktop_hub.cursor_chat.subprocess.run",
        side_effect=[
            MagicMock(stdout="/mnt/c/tmp/coords.ps1\n", returncode=0),
            MagicMock(stdout="0 0 0 0\n", stderr="", returncode=0),
        ],
    ), patch("shorts_bot.desktop_hub.cursor_chat._windows_powershell", return_value=MagicMock(is_file=lambda: True)):
        with pytest.raises(CursorChatError, match="coords are 0"):
            resolve_cursor_coords(repo_root=MagicMock(__truediv__=lambda s, x: MagicMock(is_file=lambda: True)))


def test_send_cursor_message_types_full_text(monkeypatch):
    client = MagicMock()
    client.ping.return_value = "alive"
    monkeypatch.setattr(
        "shorts_bot.desktop_hub.cursor_chat.resolve_cursor_coords",
        lambda **_: (10, 20, 30, 40),
    )
    monkeypatch.setattr("shorts_bot.desktop_hub.cursor_chat.apply_helper_env", lambda: None)
    monkeypatch.setattr("shorts_bot.desktop_hub.cursor_chat.DesktopHubClient", lambda: client)
    monkeypatch.setattr("shorts_bot.desktop_hub.cursor_chat.time.sleep", lambda _: None)

    coords = send_cursor_message("Hub CEO: full message with spaces")
    assert coords == (10, 20, 30, 40)
    client.type_text.assert_called_once_with("Hub CEO: full message with spaces")
