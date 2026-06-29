"""KeyFreeze — lock/unlock local keyboard + mouse on owner Windows hub.

KeyFreeze (free Windows app) blocks physical keyboard and mouse while the PC
stays on. The cloud agent uses the desktop helper to send the owner's private
unlock hotkey and can launch KeyFreeze when it is not already running.

Owner setup: docs/FOR_OWNER_KEYFREEZE.md
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from shorts_bot.desktop_hub.client import DesktopHubClient, DesktopHubError
from shorts_bot.desktop_hub.config import apply_helper_env, desktop_hub_dir, load_helper_env_file
from shorts_bot.desktop_hub.launcher import ensure_running, is_wsl

ROOT = Path(__file__).resolve().parents[2]
LOCK_PS1 = ROOT / "scripts" / "desktop_helper" / "keyfreeze_lock.ps1"
STATUS_PS1 = ROOT / "scripts" / "desktop_helper" / "keyfreeze_status.ps1"

DEFAULT_HOTKEY = ("ctrl", "alt", "f")
DEFAULT_COUNTDOWN_SECONDS = 6


@dataclass(frozen=True)
class KeyFreezeConfig:
    exe_path: str
    hotkey: tuple[str, ...]
    countdown_seconds: int


@dataclass(frozen=True)
class KeyFreezeStatus:
    process_running: bool
    locked: bool | None
    exe_configured: bool
    exe_path: str
    hotkey_configured: bool
    state_file: str


def state_path() -> Path:
    return desktop_hub_dir() / "keyfreeze.state.json"


def parse_hotkey(spec: str) -> tuple[str, ...]:
    """Parse 'ctrl+alt+f' or 'ctrl alt f' into normalized key names."""
    raw = spec.replace("+", " ").replace(",", " ")
    parts = [p.strip().lower() for p in raw.split() if p.strip()]
    if not parts:
        raise ValueError("KEYFREEZE_HOTKEY is empty")
    normalized: list[str] = []
    for part in parts:
        if part in {"control", "ctl"}:
            normalized.append("ctrl")
        elif part in {"command", "win", "windows", "super"}:
            normalized.append("win")
        else:
            normalized.append(part)
    return tuple(normalized)


def load_config() -> KeyFreezeConfig:
    apply_helper_env()
    file_env = load_helper_env_file()
    exe = (os.environ.get("KEYFREEZE_EXE") or file_env.get("KEYFREEZE_EXE") or "").strip()
    hotkey_raw = (
        os.environ.get("KEYFREEZE_HOTKEY") or file_env.get("KEYFREEZE_HOTKEY") or "ctrl+alt+f"
    ).strip()
    countdown_raw = (
        os.environ.get("KEYFREEZE_COUNTDOWN_SECONDS")
        or file_env.get("KEYFREEZE_COUNTDOWN_SECONDS")
        or str(DEFAULT_COUNTDOWN_SECONDS)
    ).strip()
    try:
        countdown = max(1, int(countdown_raw))
    except ValueError:
        countdown = DEFAULT_COUNTDOWN_SECONDS
    try:
        hotkey = parse_hotkey(hotkey_raw)
    except ValueError:
        hotkey = DEFAULT_HOTKEY
    return KeyFreezeConfig(exe_path=exe, hotkey=hotkey, countdown_seconds=countdown)


def read_state() -> dict[str, object]:
    path = state_path()
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def write_state(*, locked: bool) -> None:
    path = state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "locked": locked,
        "updated_at": datetime.now(UTC).isoformat(),
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _powershell_exe() -> Path | None:
    for candidate in (
        Path("/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"),
        Path("/mnt/c/WINDOWS/System32/WindowsPowerShell/v1.0/powershell.exe"),
    ):
        if candidate.is_file():
            return candidate
    return None


def _run_powershell_script(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    ps = _powershell_exe()
    if ps is None:
        raise RuntimeError("PowerShell not found — run KeyFreeze commands from WSL on the hub")
    if not script.is_file():
        raise RuntimeError(f"Missing script: {script}")
    cmd = [str(ps), "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script), *args]
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def is_process_running() -> bool:
    if os.name == "nt":
        proc = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "if (Get-Process *KeyFreeze* -ErrorAction SilentlyContinue) { exit 0 } else { exit 1 }",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        return proc.returncode == 0
    if is_wsl():
        proc = _run_powershell_script(STATUS_PS1)
        return proc.returncode == 0 and proc.stdout.strip().lower() == "running"
    return False


def launch_keyfreeze(config: KeyFreezeConfig) -> None:
    if not config.exe_path:
        raise RuntimeError(
            "KEYFREEZE_EXE not set — add path to data/desktop_hub/helper.env (see FOR_OWNER_KEYFREEZE.md)"
        )
    if os.name == "nt":
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", f'Start-Process -FilePath "{config.exe_path}"'],
            check=True,
        )
        return
    if is_wsl():
        proc = _run_powershell_script(LOCK_PS1, config.exe_path)
        if proc.returncode != 0:
            detail = (proc.stderr or proc.stdout or "").strip()
            raise RuntimeError(f"KeyFreeze launch failed: {detail}")
        return
    raise RuntimeError("KeyFreeze launch requires Windows or WSL on the hub")


def send_hotkey(client: DesktopHubClient, hotkey: tuple[str, ...]) -> None:
    client.hotkey(*hotkey)


def get_status() -> KeyFreezeStatus:
    config = load_config()
    state = read_state()
    locked_val = state.get("locked")
    locked: bool | None
    if isinstance(locked_val, bool):
        locked = locked_val
    else:
        locked = None
    return KeyFreezeStatus(
        process_running=is_process_running(),
        locked=locked,
        exe_configured=bool(config.exe_path),
        exe_path=config.exe_path,
        hotkey_configured=bool(config.hotkey),
        state_file=str(state_path()),
    )


def lock(*, force: bool = False, client: DesktopHubClient | None = None) -> str:
    """Lock keyboard + mouse. Returns a short status message."""
    config = load_config()
    state = read_state()
    currently_locked = state.get("locked") is True

    if currently_locked and not force:
        return "already locked (state file)"

    hub = client or DesktopHubClient()
    if not ensure_running(launch=True):
        raise DesktopHubError("desktop helper not running — run ensure first")

    if not is_process_running():
        launch_keyfreeze(config)
        time.sleep(config.countdown_seconds)
        write_state(locked=True)
        return f"launched KeyFreeze — locked after {config.countdown_seconds}s countdown"

    send_hotkey(hub, config.hotkey)
    time.sleep(0.4)
    write_state(locked=True)
    return "hotkey sent — input locked"


def unlock(*, force: bool = False, client: DesktopHubClient | None = None) -> str:
    """Unlock keyboard + mouse via owner's private hotkey."""
    config = load_config()
    state = read_state()
    currently_unlocked = state.get("locked") is False

    if currently_unlocked and not force:
        return "already unlocked (state file)"

    hub = client or DesktopHubClient()
    if not ensure_running(launch=True):
        raise DesktopHubError("desktop helper not running — run ensure first")

    send_hotkey(hub, config.hotkey)
    time.sleep(0.4)
    write_state(locked=False)
    return "hotkey sent — input unlocked"
