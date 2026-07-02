#!/usr/bin/env python3
"""Apply Kalodata filters on hub — Playwright DOM + verify-before-submit gates."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shorts_bot.tiktok_shop.kalodata_hub_session import main

if __name__ == "__main__":
    raise SystemExit(main())
