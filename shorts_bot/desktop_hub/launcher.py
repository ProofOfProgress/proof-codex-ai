"""Start desktop helper on Windows from WSL or verify it is running."""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

from shorts_bot.desktop_hub.client import DesktopHubClient, DesktopHubError
from shorts_bot.desktop_hub.config import apply_helper_env, daemon_pid_path

ROOT = Path(__file__).resolve().parents[2]
LAUNCH_PS1 = ROOT / "scripts" / "desktop_helper_start_background.ps1"
ENSURE_SH = ROOT / "scripts" / "desktop_helper_ensure.sh"


def _powershell_exe() -> Path | None:
    for candidate in (
        Path("/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"),
        Path("/mnt/c/WINDOWS/System32/WindowsPowerShell/v1.0/powershell.exe"),
    ):
        if candidate.is_file():
            return candidate
    return None


def is_wsl() -> bool:
    return Path("/proc/version").is_file() and "microsoft" in Path("/proc/version").read_text().lower()


def ping_helper(*, timeout: float = 3.0) -> bool:
    apply_helper_env()
    try:
        DesktopHubClient(timeout=timeout).ping()
        return True
    except DesktopHubError:
        return False


def launch_windows_helper(*, wait_seconds: float = 3.0) -> None:
    """Start helper daemon on Windows (detached). Raises if launch fails."""
    ps = _powershell_exe()
    if ps is None:
        raise RuntimeError("PowerShell not found — run START_HELPER.bat on Windows instead")

    win_repo = subprocess.check_output(["wslpath", "-w", str(ROOT)], text=True).strip()
    ps1_win = subprocess.check_output(["wslpath", "-w", str(LAUNCH_PS1)], text=True).strip()
    proc = subprocess.run(
        [
            str(ps),
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-WindowStyle",
            "Hidden",
            "-File",
            ps1_win,
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        raise RuntimeError(f"desktop helper launch failed: {detail}")

    if wait_seconds > 0:
        time.sleep(wait_seconds)


def ensure_running(*, launch: bool = True, wait_seconds: float = 5.0) -> bool:
    """Ping helper; optionally launch from WSL if down."""
    apply_helper_env()
    if ping_helper(timeout=2.0):
        return True
    if not launch:
        return False
    if not is_wsl() and os.name != "nt":
        return False
    if is_wsl():
        launch_windows_helper(wait_seconds=wait_seconds)
    else:
        # Windows native — start background ps1
        subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(LAUNCH_PS1),
            ],
            cwd=str(ROOT),
            check=True,
        )
        if wait_seconds > 0:
            time.sleep(wait_seconds)
    return ping_helper(timeout=max(5.0, wait_seconds))


def ensure_via_hub_ssh() -> int:
    """Cloud agent: run ensure script on owner hub over SSH."""
    from shorts_bot.hub_remote import run_remote

    if not ENSURE_SH.is_file():
        return 1
    return run_remote(["cd /home/isaac/proof-codex-ai && bash scripts/desktop_helper_ensure.sh"])
