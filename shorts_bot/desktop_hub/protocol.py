"""JSON command protocol for the Windows desktop helper daemon."""

from __future__ import annotations

from typing import Any

ALLOWED_ACTIONS = frozenset(
    {
        "type",
        "press",
        "hotkey",
        "click",
        "move",
        "screenshot",
        "ping",
    }
)


def validate_command(body: dict[str, Any]) -> dict[str, Any]:
    action = str(body.get("action", "")).strip().lower()
    if action not in ALLOWED_ACTIONS:
        raise ValueError(f"unknown action: {action}")

    if action == "type":
        text = body.get("text")
        if not isinstance(text, str):
            raise ValueError("type requires string 'text'")
        return {"action": action, "text": text}

    if action == "press":
        key = body.get("key")
        if not isinstance(key, str) or not key.strip():
            raise ValueError("press requires string 'key'")
        return {"action": action, "key": key.strip()}

    if action == "hotkey":
        keys = body.get("keys")
        if not isinstance(keys, list) or not keys or not all(isinstance(k, str) for k in keys):
            raise ValueError("hotkey requires list 'keys'")
        return {"action": action, "keys": [k.strip() for k in keys if k.strip()]}

    if action in ("click", "move"):
        for field in ("x", "y"):
            if not isinstance(body.get(field), (int, float)):
                raise ValueError(f"{action} requires numeric '{field}'")
        cmd: dict[str, Any] = {"action": action, "x": int(body["x"]), "y": int(body["y"])}
        if action == "click":
            button = str(body.get("button", "left")).lower()
            if button not in ("left", "right", "middle"):
                raise ValueError("click button must be left, right, or middle")
            cmd["button"] = button
            if "clicks" in body:
                cmd["clicks"] = max(1, int(body["clicks"]))
        return cmd

    if action == "screenshot":
        return {"action": action}

    return {"action": "ping"}
