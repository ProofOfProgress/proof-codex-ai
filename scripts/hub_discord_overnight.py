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

    # Fresh process avoids Playwright sync/async conflict on some hub shells.
    proc = subprocess.run(
        [sys.executable, "-c", "from shorts_bot.browser.discord_session import crawl_discord; print(crawl_discord(scroll_passes=10))"],
        cwd=ROOT,
        env={k: v for k, v in __import__("os").environ.items()},
    )
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
