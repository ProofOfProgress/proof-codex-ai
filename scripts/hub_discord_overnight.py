#!/usr/bin/env python3
"""Hub: Discord read-only crawl → inbox markdown."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    from shorts_bot.browser.discord_session import crawl_discord

    out = crawl_discord(scroll_passes=10)
    print(f"OK discord crawl → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
