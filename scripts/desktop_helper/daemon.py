#!/usr/bin/env python3
"""
Windows desktop helper daemon — keyboard + mouse for cloud agent via local HTTP.

Run on the **Windows** side of the hub laptop (logged-in session):
  python scripts/desktop_helper/daemon.py

WSL / cloud agent sends JSON commands (type, hotkey, click, screenshot).
Requires: pip install -r scripts/desktop_helper/requirements.txt
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

# Allow importing protocol from repo when run from repo root
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shorts_bot.desktop_hub.protocol import validate_command  # noqa: E402

try:
    from pynput.keyboard import Controller as KeyboardController
    from pynput.keyboard import Key
    from pynput.mouse import Button, Controller as MouseController
except ImportError:
    KeyboardController = None  # type: ignore[misc, assignment]
    Key = None  # type: ignore[misc, assignment]
    Button = None  # type: ignore[misc, assignment]
    MouseController = None  # type: ignore[misc, assignment]

try:
    import mss
except ImportError:
    mss = None  # type: ignore[assignment]

KEY_ALIASES: dict[str, str] = {
    "enter": "enter",
    "return": "enter",
    "tab": "tab",
    "esc": "esc",
    "escape": "esc",
    "space": "space",
    "backspace": "backspace",
    "delete": "delete",
    "up": "up",
    "down": "down",
    "left": "left",
    "right": "right",
    "home": "home",
    "end": "end",
    "pageup": "page_up",
    "pagedown": "page_down",
}


def _resolve_key(name: str):
    if Key is None:
        raise RuntimeError("pynput not installed")
    lower = name.strip().lower()
    if lower in KEY_ALIASES:
        return getattr(Key, KEY_ALIASES[lower])
    if len(name) == 1:
        return name
    if lower.startswith("ctrl") or lower == "control":
        return Key.ctrl
    if lower.startswith("alt"):
        return Key.alt
    if lower.startswith("shift"):
        return Key.shift
    if lower.startswith("win") or lower == "cmd":
        return Key.cmd
    raise ValueError(f"unknown key: {name}")


class DesktopExecutor:
    def __init__(self) -> None:
        if KeyboardController is None or MouseController is None:
            raise RuntimeError(
                "Install helper deps: pip install -r scripts/desktop_helper/requirements.txt"
            )
        self.keyboard = KeyboardController()
        self.mouse = MouseController()

    def execute(self, cmd: dict[str, Any]) -> dict[str, Any]:
        action = cmd["action"]
        if action == "ping":
            return {"ok": True, "message": "desktop helper alive"}

        if action == "type":
            self.keyboard.type(cmd["text"])
            return {"ok": True, "message": f"typed {len(cmd['text'])} chars"}

        if action == "press":
            self.keyboard.press(_resolve_key(cmd["key"]))
            self.keyboard.release(_resolve_key(cmd["key"]))
            return {"ok": True, "message": f"pressed {cmd['key']}"}

        if action == "hotkey":
            resolved = [_resolve_key(k) for k in cmd["keys"]]
            if len(resolved) == 1:
                self.keyboard.press(resolved[0])
                self.keyboard.release(resolved[0])
            else:
                *mods, last = resolved
                with self.keyboard.pressed(*mods):
                    self.keyboard.press(last)
                    self.keyboard.release(last)
            return {"ok": True, "message": "+".join(cmd["keys"])}

        if action == "move":
            self.mouse.position = (cmd["x"], cmd["y"])
            return {"ok": True, "message": f"moved to {cmd['x']},{cmd['y']}"}

        if action == "click":
            button_name = cmd.get("button", "left")
            button = {
                "left": Button.left,
                "right": Button.right,
                "middle": Button.middle,
            }[button_name]
            self.mouse.position = (cmd["x"], cmd["y"])
            clicks = int(cmd.get("clicks", 1))
            for _ in range(clicks):
                self.mouse.click(button)
            return {"ok": True, "message": f"click {cmd['x']},{cmd['y']} x{clicks}"}

        if action == "screenshot":
            if mss is None:
                raise RuntimeError("mss not installed")
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                shot = sct.grab(monitor)
                png = mss.tools.to_png(shot.rgb, shot.size)
            return {
                "ok": True,
                "width": shot.width,
                "height": shot.height,
                "png_base64": base64.standard_b64encode(png).decode("ascii"),
            }

        raise ValueError(f"unhandled action: {action}")


def make_handler(token: str, executor: DesktopExecutor):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args: object) -> None:
            sys.stderr.write(f"[desktop_helper] {self.address_string()} {fmt % args}\n")

        def _send_json(self, code: int, payload: dict[str, Any]) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self) -> None:
            if self.path != "/v1/command":
                self._send_json(404, {"ok": False, "error": "not found"})
                return
            auth = self.headers.get("Authorization", "")
            if auth != f"Bearer {token}":
                self._send_json(401, {"ok": False, "error": "unauthorized"})
                return
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length)
            try:
                body = json.loads(raw.decode("utf-8"))
                cmd = validate_command(body)
                result = executor.execute(cmd)
                self._send_json(200, result)
            except (ValueError, json.JSONDecodeError) as exc:
                self._send_json(400, {"ok": False, "error": str(exc)})
            except Exception as exc:
                self._send_json(500, {"ok": False, "error": str(exc)})

    return Handler


def main() -> int:
    parser = argparse.ArgumentParser(description="Windows desktop helper daemon")
    parser.add_argument("--host", default=os.environ.get("DESKTOP_HELPER_BIND", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("DESKTOP_HELPER_PORT", "9876")))
    args = parser.parse_args()

    token = (os.environ.get("DESKTOP_HELPER_TOKEN") or "").strip()
    if not token:
        print("Set DESKTOP_HELPER_TOKEN before starting the daemon.", file=sys.stderr)
        return 1

    executor = DesktopExecutor()
    handler = make_handler(token, executor)
    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"Desktop helper listening on http://{args.host}:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
