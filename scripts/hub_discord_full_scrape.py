#!/usr/bin/env python3
"""Hard Discord scrape — all servers/channels via desktop helper (screenshots only)."""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from shorts_bot.config import settings
from shorts_bot.desktop_hub.client import DesktopHubClient

SHOT = settings.data_dir / "desktop_hub" / "discord_full"
SERVER_X = 36
SERVER_YS = (75, 150, 225, 300, 375)
CHANNEL_X = 230
CHANNEL_YS = (150, 220, 290, 360, 430)


def _cli(*args: str) -> None:
    subprocess.run(
        [sys.executable, "-m", "shorts_bot.desktop_hub.cli", *args],
        cwd=ROOT,
        check=True,
    )


def main() -> int:
    client = DesktopHubClient()
    client.ping()
    SHOT.mkdir(parents=True, exist_ok=True)

    _cli("hotkey", "win", "1")
    time.sleep(1.0)
    client.click(960, 540)
    time.sleep(0.5)

    n = 0
    for si, sy in enumerate(SERVER_YS):
        client.click(SERVER_X, sy)
        time.sleep(1.2)
        for ci, cy in enumerate(CHANNEL_YS):
            client.click(CHANNEL_X, cy)
            time.sleep(0.9)
            for scroll in range(0, 24, 4):
                path = SHOT / f"s{si:02d}_c{ci:02d}_u{scroll:03d}.png"
                path.write_bytes(client.screenshot().png_bytes)
                n += 1
                for _ in range(4):
                    client.press("pageup")
                    time.sleep(0.35)

    print(f"OK {n} screenshots → {SHOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
