#!/usr/bin/env python3
"""Pull latest desktop screenshot from hub to local workspace."""
from __future__ import annotations

import base64
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "desktop_hub" / "owner_screen_now.png"
REMOTE = os.environ.get("HUB_SCREENSHOT_REMOTE", "~/proof-codex-ai/data/desktop_hub/owner_screen_now.png")


def main() -> int:
    remote = REMOTE.replace("~/", "")
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "shorts_bot.hub_remote",
            "run",
            f"base64 -w0 ~/{remote}" if remote.startswith("proof") else f"base64 -w0 {REMOTE}",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    lines = [ln for ln in proc.stdout.splitlines() if ln and not ln.startswith("Tailscale")]
    if not lines:
        print(proc.stderr or proc.stdout, file=sys.stderr)
        return 1
    raw = "".join(lines)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(base64.b64decode(raw))
    print(f"OK {OUT} ({OUT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
