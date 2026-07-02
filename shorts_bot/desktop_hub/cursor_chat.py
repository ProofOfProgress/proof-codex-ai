"""Type into Cursor chat on the hub via desktop helper."""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path

from shorts_bot.desktop_hub.client import DesktopHubClient, DesktopHubError

REPO_ROOT = Path(__file__).resolve().parents[2]
PS_EXE = Path("/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe")
HELPER_ENV = REPO_ROOT / "data" / "desktop_hub" / "helper.env"
SCHEDULE_JSON = REPO_ROOT / "data" / "desktop_hub" / "schedule.json"


class CursorChatError(DesktopHubError):
    """Cursor chat automation failed."""


def _load_helper_env() -> None:
    if not HELPER_ENV.is_file():
        return
    for line in HELPER_ENV.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        val = val.strip().strip('"').strip("'")
        if key.strip() == "DESKTOP_HELPER_TOKEN":
            val = "".join(val.split())
        os.environ.setdefault(key.strip(), val)


def _coords_from_schedule() -> tuple[int, int, int, int] | None:
    if not SCHEDULE_JSON.is_file():
        return None
    try:
        raw = json.loads(SCHEDULE_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    block = raw.get("daily_prelaunch") or {}
    ix = int(block.get("focus_x") or 0)
    iy = int(block.get("focus_y") or 0)
    sx = int(block.get("submit_x") or 0)
    sy = int(block.get("submit_y") or 0)
    if ix > 0 and iy > 0 and sx > 0 and sy > 0:
        return ix, iy, sx, sy
    return None


def _windows_powershell() -> Path:
    if not PS_EXE.is_file():
        raise CursorChatError(f"Windows PowerShell not found at {PS_EXE} (run from WSL on hub)")
    return PS_EXE


def resolve_cursor_coords(*, repo_root: Path | None = None) -> tuple[int, int, int, int]:
    """Return input_x, input_y, send_x, send_y for Cursor composer."""
    calibrated = _coords_from_schedule()
    if calibrated:
        return calibrated

    root = repo_root or REPO_ROOT
    ps1 = root / "scripts" / "hub_cursor_window_coords.ps1"
    if not ps1.is_file():
        raise CursorChatError(f"Missing coords script: {ps1}")

    ps1_win = subprocess.run(
        ["wslpath", "-w", str(ps1)],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    ps = _windows_powershell()
    proc = subprocess.run(
        [str(ps), "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ps1_win],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "coords script failed").strip()
        raise CursorChatError(detail)
    parts = proc.stdout.strip().split()
    if len(parts) != 4:
        raise CursorChatError(f"Unexpected coords output: {proc.stdout!r}")
    ix, iy, sx, sy = (int(x) for x in parts)
    if min(ix, iy, sx, sy) <= 0:
        raise CursorChatError(
            "Cursor window coords are 0 — click Cursor on the hub so the chat box is visible, then retry"
        )
    return ix, iy, sx, sy


def _focus_cursor_window(*, repo_root: Path | None = None) -> None:
    root = repo_root or REPO_ROOT
    ps1 = root / "scripts" / "hub_cursor_focus.ps1"
    if not ps1.is_file():
        raise CursorChatError(f"Missing focus script: {ps1}")
    ps1_win = subprocess.run(
        ["wslpath", "-w", str(ps1)],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    ps = _windows_powershell()
    proc = subprocess.run(
        [str(ps), "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ps1_win],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "focus script failed").strip()
        raise CursorChatError(detail)


def send_cursor_message(message: str, *, repo_root: Path | None = None) -> tuple[int, int, int, int]:
    """Focus Cursor chat, type message, submit. Returns coords used (or -1 for hotkey path)."""
    text = message.strip()
    if not text:
        raise CursorChatError("message is empty")

    _load_helper_env()
    client = DesktopHubClient()
    client.ping()

    calibrated = _coords_from_schedule()
    if calibrated:
        ix, iy, sx, sy = calibrated
        _focus_cursor_window(repo_root=repo_root)
        time.sleep(0.35)
        client.click(ix, iy)
        time.sleep(0.35)
        client.type_text(text)
        time.sleep(0.35)
        client.click(sx, sy)
        return ix, iy, sx, sy

    # Default: assume Cursor is open on the hub. Ctrl+L opens chat, Enter sends.
    # (Focus script often fails over SSH — different Windows session than your desktop.)
    client.hotkey("ctrl", "l")
    time.sleep(0.55)
    client.type_text(text)
    time.sleep(0.25)
    client.press("enter")
    return -1, -1, -1, -1


def cursor_send_via_hub(message: str) -> int:
    """Cloud CEO: run cursor-send on owner hub over SSH."""
    import base64

    from shorts_bot.hub_remote import run_remote

    text = message.strip()
    if not text:
        return 2
    b64 = base64.b64encode(text.encode("utf-8")).decode("ascii")
    # hub_run_ssh wraps port-2222 commands into WSL bash -lc; no extra bash layer needed.
    return run_remote(["python3", "scripts/hub_cursor_send.py", "--msg-b64", b64])
