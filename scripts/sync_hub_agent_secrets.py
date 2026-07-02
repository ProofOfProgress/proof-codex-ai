#!/usr/bin/env python3
"""Sync cloud VM secrets into hub data/agent_credentials.env (gitignored)."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shorts_bot.config import settings

HUB_MIRROR_KEYS = (
    "GEMINI_API_KEY",
    "GEMINI_MODEL",
    "KALODATA_PILOT_TOKEN",
    "KALODATA_REGION",
    "SCOUT_PROVIDER",
)


def main() -> int:
    synced = 0
    for key in HUB_MIRROR_KEYS:
        val = (os.environ.get(key) or getattr(settings, key.lower(), None) or "")
        val = str(val).strip()
        if not val:
            continue
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "shorts_bot.hub_remote",
                "run",
                "--",
                "cd ~/proof-codex-ai && python3 scripts/patch_agent_credentials.py",
                f"--key={key}",
                f"--value={val}",
            ],
            cwd=ROOT,
            text=True,
        )
        if proc.returncode != 0:
            print(f"WARN failed sync {key}", file=sys.stderr)
        else:
            synced += 1
    print(f"Synced {synced} key(s) to hub agent_credentials.env")
    return 0 if synced else 1


if __name__ == "__main__":
    raise SystemExit(main())
