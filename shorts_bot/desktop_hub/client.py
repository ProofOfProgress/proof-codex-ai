"""HTTP client for the Windows desktop helper daemon."""

from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from shorts_bot.desktop_hub.host import helper_base_url
from shorts_bot.desktop_hub.protocol import validate_command


class DesktopHubError(RuntimeError):
    """Desktop helper request failed."""


@dataclass
class ScreenshotResult:
    width: int
    height: int
    png_bytes: bytes


class DesktopHubClient:
    def __init__(
        self,
        *,
        base_url: str | None = None,
        token: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.base_url = (base_url or helper_base_url()).rstrip("/")
        self.token = token or os.environ.get("DESKTOP_HELPER_TOKEN", "")
        self.timeout = timeout

    def _request(self, command: dict[str, Any]) -> dict[str, Any]:
        if not self.token:
            raise DesktopHubError(
                "DESKTOP_HELPER_TOKEN not set — add to Cursor Secrets and start a new agent run"
            )
        payload = json.dumps(validate_command(command)).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/v1/command",
            data=payload,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                body = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise DesktopHubError(f"helper HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise DesktopHubError(
                f"cannot reach desktop helper at {self.base_url} — is it running on Windows?"
            ) from exc
        try:
            data = json.loads(body)
        except json.JSONDecodeError as exc:
            raise DesktopHubError(f"invalid JSON from helper: {body[:200]}") from exc
        if not data.get("ok"):
            raise DesktopHubError(str(data.get("error") or "helper returned ok=false"))
        return data

    def ping(self) -> str:
        return str(self._request({"action": "ping"}).get("message", "pong"))

    def type_text(self, text: str) -> None:
        self._request({"action": "type", "text": text})

    def press(self, key: str) -> None:
        self._request({"action": "press", "key": key})

    def hotkey(self, *keys: str) -> None:
        self._request({"action": "hotkey", "keys": list(keys)})

    def click(self, x: int, y: int, *, button: str = "left", clicks: int = 1) -> None:
        self._request({"action": "click", "x": x, "y": y, "button": button, "clicks": clicks})

    def move(self, x: int, y: int) -> None:
        self._request({"action": "move", "x": x, "y": y})

    def screenshot(self) -> ScreenshotResult:
        data = self._request({"action": "screenshot"})
        raw = data.get("png_base64")
        if not isinstance(raw, str):
            raise DesktopHubError("screenshot missing png_base64")
        png = base64.b64decode(raw)
        return ScreenshotResult(
            width=int(data.get("width") or 0),
            height=int(data.get("height") or 0),
            png_bytes=png,
        )
