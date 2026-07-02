#!/usr/bin/env python3
"""Hub: Discord read-only crawl → inbox markdown."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    import subprocess

    proc = subprocess.run(
        [sys.executable, "-m", "shorts_bot.browser.cli", "crawl-discord"],
        cwd=ROOT,
    )
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
