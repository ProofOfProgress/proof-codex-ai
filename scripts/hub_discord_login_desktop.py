#!/usr/bin/env python3
"""Discord login on Edge via desktop helper + Gemini click hints (hub)."""

from __future__ import annotations

import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from shorts_bot.config import settings
from shorts_bot.desktop_hub.client import DesktopHubClient, DesktopHubError

SHOT = settings.data_dir / "desktop_hub" / "discord_login_step.png"
LOGIN_URL = "https://discord.com/login"


def _cli(*args: str) -> None:
    subprocess.run(
        [sys.executable, "-m", "shorts_bot.desktop_hub.cli", *args],
        cwd=ROOT,
        check=True,
    )


def _gemini_click(image_path: Path, goal: str) -> tuple[int, int] | None:
    key = (settings.gemini_api_key or "").strip()
    if not key:
        return None
    try:
        from google import genai
    except ImportError:
        return None
    client = genai.Client(api_key=key)
    model = (settings.gemini_model or "gemini-2.5-flash-lite").strip()
    prompt = (
        f"Goal: {goal}\n"
        "Return ONLY one line: CLICK x y  (pixel coords on this screenshot). "
        "If not found: SKIP"
    )
    try:
        resp = client.models.generate_content(
            model=model,
            contents=[prompt, genai.types.Part.from_bytes(data=image_path.read_bytes(), mime_type="image/png")],
        )
        text = (resp.text or "").strip()
    except Exception:
        return None
    m = re.search(r"CLICK\s+(\d+)\s+(\d+)", text, re.I)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None


def _shot(client: DesktopHubClient) -> Path:
    SHOT.parent.mkdir(parents=True, exist_ok=True)
    SHOT.write_bytes(client.screenshot().png_bytes)
    return SHOT


def _click_goal(client: DesktopHubClient, goal: str) -> bool:
    path = _shot(client)
    pt = _gemini_click(path, goal)
    if not pt:
        return False
    client.click(pt[0], pt[1])
    time.sleep(0.6)
    return True


def _load_creds() -> tuple[str, str]:
    import os

    cred = settings.data_dir / "agent_credentials.env"
    if cred.is_file():
        for line in cred.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, _, v = line.partition("=")
                k, v = k.strip(), v.strip().strip('"').strip("'")
                if v and k not in os.environ:
                    os.environ[k] = v
    email = (os.environ.get("DISCORD_LOGIN_EMAIL") or "").strip()
    password = (os.environ.get("DISCORD_LOGIN_PASSWORD") or "").strip()
    if not email or not password:
        raise RuntimeError("DISCORD_LOGIN_EMAIL/PASSWORD missing in agent_credentials.env")
    return email, password


def login_discord_desktop() -> None:
    email, password = _load_creds()
    client = DesktopHubClient()
    client.ping()

    # Open Discord login in default browser
    _cli("hotkey", "win", "r")
    time.sleep(0.8)
    _cli("type", LOGIN_URL)
    _cli("press", "enter")
    time.sleep(4)

    # Email field
    if not _click_goal(client, "Click the Email or Phone Number input field on Discord login page"):
        client.click(700, 420)
    time.sleep(0.3)
    _cli("hotkey", "ctrl", "a")
    client.type_text(email)
    time.sleep(0.4)

    # Password field
    if not _click_goal(client, "Click the Password input field on Discord login page"):
        client.click(700, 500)
    time.sleep(0.3)
    _cli("hotkey", "ctrl", "a")
    client.type_text(password)
    time.sleep(0.5)

    # hCaptcha — "I am human" checkbox
    for goal in (
        "Click the hCaptcha 'I am human' checkbox",
        "Click the checkbox that says I am human or verify you are human",
        "Click the CAPTCHA checkbox below the password field",
    ):
        if _click_goal(client, goal):
            time.sleep(2.5)
            break

    # Log In button
    _click_goal(client, "Click the blue Log In button on Discord login page")
    time.sleep(6)

    path = _shot(client)
    body_hint = path.read_bytes()
    print(f"Screenshot after login: {path} ({len(body_hint)} bytes)")
    print("If still on login page, CAPTCHA may need a second click — re-run or complete manually once.")


if __name__ == "__main__":
    login_discord_desktop()
