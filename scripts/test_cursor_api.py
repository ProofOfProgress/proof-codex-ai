#!/usr/bin/env python3
"""Probe Cursor Cloud Agent API — only reports what HTTP returns."""

from __future__ import annotations

import base64
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env"


def _load_key() -> str | None:
    key = (os.environ.get("CURSOR_API_KEY") or "").strip()
    if key:
        return key
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            if line.startswith("CURSOR_API_KEY="):
                v = line.split("=", 1)[1].strip()
                if v and "your" not in v.lower():
                    return v
    return None


def _request(method: str, path: str, key: str, body: dict | None = None) -> tuple[int, dict | str]:
    url = f"https://api.cursor.com{path}"
    headers = {"Authorization": f"Basic {base64.b64encode(f'{key}:'.encode()).decode()}"}
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            try:
                return resp.status, json.loads(raw)
            except json.JSONDecodeError:
                return resp.status, raw[:500]
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")[:500]
        try:
            return exc.code, json.loads(raw)
        except json.JSONDecodeError:
            return exc.code, raw


def main() -> int:
    key = _load_key()
    print("=== Cursor API probe ===")
    print(f"CURSOR_API_KEY in env: {'yes' if os.environ.get('CURSOR_API_KEY') else 'no'}")
    print(f"CURSOR_API_KEY in .env: {'yes' if ENV_PATH.exists() and 'CURSOR_API_KEY=' in ENV_PATH.read_text() else 'no'}")
    all_names = os.environ.get("CLOUD_AGENT_ALL_SECRET_NAMES", "")
    print(f"CURSOR_API_KEY in CLOUD_AGENT_ALL_SECRET_NAMES: {'yes' if 'CURSOR_API_KEY' in all_names else 'no'}")
    if not key:
        print("\nRESULT: Cannot test API — CURSOR_API_KEY not available on this VM.")
        return 1

    print(f"Key length: {len(key)} chars (value not printed)\n")

    tests = [
        ("GET", "/v1/me", None, "Auth / key info"),
        ("GET", "/v1/models", None, "List models"),
        ("GET", "/v1/agents", None, "List agents"),
    ]
    for method, path, body, label in tests:
        code, payload = _request(method, path, key, body)
        print(f"[{label}] {method} {path} → HTTP {code}")
        if isinstance(payload, dict):
            # Redact anything that looks sensitive
            safe = {k: payload[k] for k in list(payload.keys())[:8]}
            print(json.dumps(safe, indent=2)[:800])
        else:
            print(str(payload)[:400])
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
