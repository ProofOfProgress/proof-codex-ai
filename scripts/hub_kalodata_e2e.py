#!/usr/bin/env python3
"""Hub end-to-end: Edge CDP → Kalodata filters → scout → quality validate."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-Command",
            'Start-Process msedge -ArgumentList "--remote-debugging-port=9222","https://www.kalodata.com/product"',
        ],
        check=False,
    )
    time.sleep(12)

    import urllib.request

    from shorts_bot.tiktok_shop.kalodata_edge_cdp import cdp_url

    cdp = cdp_url()
    try:
        urllib.request.urlopen(f"{cdp}/json/version", timeout=8)
        print(f"OK Edge CDP up at {cdp}")
    except Exception as exc:
        print(f"WARN CDP not ready at {cdp}: {exc}")

    from shorts_bot.tiktok_shop.kalodata_playwright_apply import run_verified_apply

    res = run_verified_apply(
        method="middle_core",
        category="Furniture",
        scout_limit=10,
        save_url=True,
    )
    print(res.message)
    if res.filter_url:
        print(f"URL: {res.filter_url[:120]}")

    from shorts_bot.tiktok_shop.scout_autorun import main as autorun_main

    try:
        autorun_main()
    except SystemExit as exc:
        if exc.code:
            print(f"autorun exit {exc.code}", flush=True)
    except RuntimeError as exc:
        print(f"autorun: {exc}", flush=True)

    from shorts_bot.tiktok_shop.product_scout import load_products

    print(f"products.json count: {len(load_products())}")
    subprocess.run([sys.executable, "-m", "shorts_bot.tiktok_shop.scout_cli", "validate"], check=False)
    return 0 if res.ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
