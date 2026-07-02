#!/usr/bin/env python3
"""Discord scrape — Momentum Academy server only (white M icon, left sidebar)."""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from shorts_bot.config import settings
from shorts_bot.desktop_hub.client import DesktopHubClient

SHOT = settings.data_dir / "desktop_hub" / "discord_momentum"
# Three servers left: A, M (white bg = Momentum), black — try each; M often 2nd
MOMENTUM_SERVER_YS = (110, 165, 220)
CHANNEL_X = 240
CHANNEL_YS = range(130, 520, 42)


def main() -> int:
    client = DesktopHubClient()
    client.ping()
    SHOT.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [sys.executable, "-m", "shorts_bot.desktop_hub.cli", "hotkey", "win", "1"],
        cwd=ROOT,
        check=True,
    )
    time.sleep(1.0)
    client.click(960, 400)
    time.sleep(0.5)

    n = 0
    for sy in MOMENTUM_SERVER_YS:
        client.click(36, sy)
        time.sleep(1.0)
        for cy in CHANNEL_YS:
            client.click(CHANNEL_X, cy)
            time.sleep(0.7)
            for scroll in range(0, 28, 4):
                path = SHOT / f"m_{sy}_{cy}_{scroll:03d}.png"
                path.write_bytes(client.screenshot().png_bytes)
                n += 1
                for _ in range(4):
                    client.press("pageup")
                    time.sleep(0.3)

    print(f"OK {n} Momentum-server screenshots → {SHOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
