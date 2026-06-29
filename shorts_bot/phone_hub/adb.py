"""ADB subprocess wrapper for phone hub (runs on owner WSL laptop)."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass


class AdbError(RuntimeError):
    """ADB command failed or adb binary missing."""


@dataclass(frozen=True)
class AdbResult:
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


def adb_path() -> str:
    path = shutil.which("adb")
    if not path:
        raise AdbError("adb not found — run: bash scripts/hub_adb_install.sh on the hub laptop")
    return path


def run_adb(
    *args: str,
    serial: str | None = None,
    timeout: int = 30,
    check: bool = False,
) -> AdbResult:
    cmd = [adb_path()]
    if serial:
        cmd.extend(["-s", serial])
    cmd.extend(args)
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise AdbError(f"adb timed out after {timeout}s: {' '.join(cmd)}") from exc
    except OSError as exc:
        raise AdbError(f"adb failed to start: {exc}") from exc
    result = AdbResult(proc.returncode, proc.stdout.strip(), proc.stderr.strip())
    if check and not result.ok:
        detail = result.stderr or result.stdout or f"exit {result.returncode}"
        raise AdbError(f"adb {' '.join(args)} failed: {detail}")
    return result


def adb_version() -> str:
    result = run_adb("version", check=True)
    return result.stdout.splitlines()[0] if result.stdout else "unknown"


def list_devices() -> list[tuple[str, str]]:
    """Return [(serial, state), ...] from ``adb devices``."""
    result = run_adb("devices", check=True)
    rows: list[tuple[str, str]] = []
    for line in result.stdout.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 2 and parts[1] != "offline":
            rows.append((parts[0], parts[1]))
    return rows


def device_ready(serial: str) -> bool:
    for dev_serial, state in list_devices():
        if dev_serial == serial and state == "device":
            return True
    return False
