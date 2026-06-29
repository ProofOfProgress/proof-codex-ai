"""Tests for desktop hub protocol and client."""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from shorts_bot.desktop_hub.client import DesktopHubClient, DesktopHubError
from shorts_bot.desktop_hub.host import windows_host_from_wsl
from shorts_bot.desktop_hub.protocol import validate_command


def test_validate_type_command():
    cmd = validate_command({"action": "type", "text": "hello"})
    assert cmd == {"action": "type", "text": "hello"}


def test_validate_rejects_unknown():
    with pytest.raises(ValueError):
        validate_command({"action": "explode"})


def test_validate_click():
    cmd = validate_command({"action": "click", "x": 10, "y": 20})
    assert cmd["x"] == 10


class _Handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        auth = self.headers.get("Authorization", "")
        if auth != "Bearer test-token":
            self.send_response(401)
            self.end_headers()
            return
        length = int(self.headers.get("Content-Length", "0"))
        body = json.loads(self.rfile.read(length).decode("utf-8"))
        if body.get("action") == "ping":
            payload = json.dumps({"ok": True, "message": "pong"}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        self.send_response(400)
        self.end_headers()

    def log_message(self, fmt: str, *args: object) -> None:
        pass


def test_client_ping_ok():
    server = HTTPServer(("127.0.0.1", 0), _Handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        client = DesktopHubClient(base_url=f"http://127.0.0.1:{port}", token="test-token")
        assert client.ping() == "pong"
    finally:
        server.shutdown()


def test_client_ping_unauthorized():
    server = HTTPServer(("127.0.0.1", 0), _Handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with pytest.raises(DesktopHubError):
            DesktopHubClient(base_url=f"http://127.0.0.1:{port}", token="wrong").ping()
    finally:
        server.shutdown()


def test_windows_host_optional():
    host = windows_host_from_wsl()
    assert host is None or host.count(".") == 3
