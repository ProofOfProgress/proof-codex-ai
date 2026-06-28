"""Low-level ADB helpers for TikTok phone automation."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from shorts_bot.tiktok.sounds import TIKTOK_PACKAGES


@dataclass
class AdbResult:
    ok: bool
    stdout: str
    stderr: str
    command: str


class AdbError(RuntimeError):
    def __init__(self, message: str, result: AdbResult | None = None) -> None:
        super().__init__(message)
        self.result = result


class AdbClient:
    def __init__(self, device_id: str | None = None) -> None:
        self.device_id = (device_id or "").strip()

    def _base(self) -> list[str]:
        cmd = ["adb"]
        if self.device_id:
            cmd.extend(["-s", self.device_id])
        return cmd

    def run(self, *args: str, check: bool = True) -> AdbResult:
        command = self._base() + list(args)
        try:
            proc = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=120,
            )
        except FileNotFoundError:
            result = AdbResult(
                ok=False,
                stdout="",
                stderr="adb not found — install Android platform-tools",
                command=" ".join(command),
            )
            if check:
                raise AdbError(result.stderr, result)
            return result
        result = AdbResult(
            ok=proc.returncode == 0,
            stdout=(proc.stdout or "").strip(),
            stderr=(proc.stderr or "").strip(),
            command=" ".join(command),
        )
        if check and not result.ok:
            raise AdbError(
                f"ADB failed ({proc.returncode}): {result.stderr or result.stdout}",
                result,
            )
        return result

    def devices(self) -> list[str]:
        out = self.run("devices", check=False).stdout
        serials: list[str] = []
        for line in out.splitlines():
            if not line.strip() or line.startswith("List of"):
                continue
            parts = line.split()
            if len(parts) >= 2 and parts[1] == "device":
                serials.append(parts[0])
        return serials

    def ensure_device(self) -> str:
        if self.device_id:
            return self.device_id
        serials = self.devices()
        if not serials:
            raise AdbError("No Android device found. Plug in phone + enable USB debugging.")
        if len(serials) > 1:
            raise AdbError(
                f"Multiple devices: {', '.join(serials)}. Set TIKTOK_ADB_DEVICE_ID or pass --device."
            )
        self.device_id = serials[0]
        return self.device_id

    def shell(self, command: str, *, check: bool = True) -> AdbResult:
        return self.run("shell", command, check=check)

    def push(self, local: Path, remote: str) -> AdbResult:
        return self.run("push", str(local), remote)

    def open_deep_link(self, uri: str, packages: Sequence[str] = TIKTOK_PACKAGES) -> str:
        """Start TikTok with a deep link; returns package that launched."""
        for package in packages:
            result = self.shell(
                f"am start -a android.intent.action.VIEW -d '{uri}' -p {package}",
                check=False,
            )
            combined = f"{result.stdout}\n{result.stderr}"
            if result.ok and "Error" not in combined:
                return package
        raise AdbError(f"Could not open deep link in TikTok: {uri}")

    def media_scan(self, remote_path: str) -> None:
        self.shell(
            f"am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE "
            f"-d file:///storage/emulated/0/{remote_path}",
            check=False,
        )
