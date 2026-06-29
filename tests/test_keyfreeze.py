"""Tests for KeyFreeze hub integration."""

from __future__ import annotations

from pathlib import Path
from unittest import mock

import pytest

from shorts_bot.desktop_hub import keyfreeze


def test_parse_hotkey_plus_separated():
    assert keyfreeze.parse_hotkey("ctrl+alt+f") == ("ctrl", "alt", "f")


def test_parse_hotkey_space_separated():
    assert keyfreeze.parse_hotkey("ctrl alt f") == ("ctrl", "alt", "f")


def test_parse_hotkey_normalizes_control():
    assert keyfreeze.parse_hotkey("control+alt+f") == ("ctrl", "alt", "f")


def test_parse_hotkey_empty_raises():
    with pytest.raises(ValueError):
        keyfreeze.parse_hotkey("   ")


def test_load_config_from_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("KEYFREEZE_EXE", r"C:\Tools\KeyFreeze\KeyFreeze.exe")
    monkeypatch.setenv("KEYFREEZE_HOTKEY", "ctrl+shift+l")
    cfg = keyfreeze.load_config()
    assert cfg.exe_path.endswith("KeyFreeze.exe")
    assert cfg.hotkey == ("ctrl", "shift", "l")


def test_write_and_read_state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    hub_dir = tmp_path / "desktop_hub"
    hub_dir.mkdir()
    monkeypatch.setattr(keyfreeze, "desktop_hub_dir", lambda: hub_dir)
    keyfreeze.write_state(locked=True)
    data = keyfreeze.read_state()
    assert data.get("locked") is True
    assert "updated_at" in data


def test_lock_launches_when_process_stopped(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    hub_dir = tmp_path / "desktop_hub"
    hub_dir.mkdir()
    monkeypatch.setattr(keyfreeze, "desktop_hub_dir", lambda: hub_dir)
    monkeypatch.setattr(keyfreeze, "load_config", lambda: keyfreeze.KeyFreezeConfig(
        exe_path=r"C:\Tools\KeyFreeze\KeyFreeze.exe",
        hotkey=("ctrl", "alt", "f"),
        countdown_seconds=1,
    ))
    monkeypatch.setattr(keyfreeze, "ensure_running", lambda **_: True)
    monkeypatch.setattr(keyfreeze, "is_process_running", lambda: False)
    launched: list[str] = []

    def _launch(cfg: keyfreeze.KeyFreezeConfig) -> None:
        launched.append(cfg.exe_path)

    monkeypatch.setattr(keyfreeze, "launch_keyfreeze", _launch)
    msg = keyfreeze.lock()
    assert "launched KeyFreeze" in msg
    assert launched == [r"C:\Tools\KeyFreeze\KeyFreeze.exe"]
    assert keyfreeze.read_state().get("locked") is True


def test_unlock_sends_hotkey(monkeypatch: pytest.MonkeyPatch):
    calls: list[tuple[str, ...]] = []

    class _FakeClient:
        def hotkey(self, *keys: str) -> None:
            calls.append(keys)

    monkeypatch.setattr(keyfreeze, "load_config", lambda: keyfreeze.KeyFreezeConfig(
        exe_path=r"C:\Tools\KeyFreeze\KeyFreeze.exe",
        hotkey=("ctrl", "alt", "f"),
        countdown_seconds=6,
    ))
    monkeypatch.setattr(keyfreeze, "ensure_running", lambda **_: True)
    monkeypatch.setattr(keyfreeze, "read_state", lambda: {"locked": True})
    msg = keyfreeze.unlock(client=_FakeClient())
    assert calls == [("ctrl", "alt", "f")]
    assert "unlocked" in msg


def test_lock_skips_when_already_locked(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(keyfreeze, "read_state", lambda: {"locked": True})
    msg = keyfreeze.lock()
    assert msg == "already locked (state file)"
