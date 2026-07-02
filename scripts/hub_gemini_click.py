#!/usr/bin/env python3
"""Use cloud Gemini to find click target on hub screenshot, click via desktop helper."""
from __future__ import annotations

import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from shorts_bot.config import settings
from shorts_bot.desktop_hub.client import DesktopHubClient


def gemini_click(path: Path, goal: str) -> tuple[int, int] | None:
    from google import genai

    client = genai.Client(api_key=settings.gemini_api_key)
    model = (settings.gemini_model or "gemini-2.5-flash-lite").strip()
    resp = client.models.generate_content(
        model=model,
        contents=[
            f"Goal: {goal}\nReturn ONLY: CLICK x y",
            genai.types.Part.from_bytes(data=path.read_bytes(), mime_type="image/png"),
        ],
    )
    m = re.search(r"CLICK\s+(\d+)\s+(\d+)", (resp.text or ""), re.I)
    return (int(m.group(1)), int(m.group(2))) if m else None


def hub_click(x: int, y: int) -> None:
    subprocess.run(
        [sys.executable, "-m", "shorts_bot.hub_remote", "run",
         f"cd ~/proof-codex-ai && python3 -m shorts_bot.desktop_hub.cli click {x} {y}"],
        cwd=ROOT,
        check=True,
    )


def hub_shot(remote: str) -> Path:
    local = ROOT / "data" / "desktop_hub" / Path(remote).name
    subprocess.run(
        [sys.executable, "-m", "shorts_bot.hub_remote", "run",
         f"cd ~/proof-codex-ai && python3 -m shorts_bot.desktop_hub.cli screenshot --out data/desktop_hub/{Path(remote).name}"],
        cwd=ROOT,
        check=True,
    )
    import base64
    proc = subprocess.run(
        [sys.executable, "-m", "shorts_bot.hub_remote", "run",
         f"base64 -w0 ~/proof-codex-ai/data/desktop_hub/{Path(remote).name}"],
        capture_output=True,
        text=True,
    )
    lines = [ln for ln in proc.stdout.splitlines() if ln and not ln.startswith("Tailscale")]
    local.parent.mkdir(parents=True, exist_ok=True)
    local.write_bytes(base64.b64decode("".join(lines)))
    return local


def main() -> int:
    goal = " ".join(sys.argv[1:]) or "Click the Momentum Academy Discord server icon in the left sidebar"
    shot = hub_shot("discord_nav.png")
    pt = gemini_click(shot, goal)
    if not pt:
        print("SKIP no coords", file=sys.stderr)
        return 1
    hub_click(pt[0], pt[1])
    print(f"clicked {pt[0]},{pt[1]} for: {goal}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
