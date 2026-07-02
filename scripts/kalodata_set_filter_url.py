#!/usr/bin/env python3
"""Owner helper: paste a Kalodata filter URL into kalodata_filters.json."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILTERS = ROOT / "data" / "tiktok_shop" / "kalodata_filters.json"

PRESETS = ("middle_core", "two_hundred", "hardcore_lurkers", "hundred_gap")


def main() -> int:
    parser = argparse.ArgumentParser(description="Save Kalodata filter URL for a scout preset")
    parser.add_argument("preset", choices=PRESETS, help="Which course filter preset")
    parser.add_argument("url", help="Full browser URL after Apply in Kalodata")
    parser.add_argument("--list", action="store_true", help="Show which presets still need URLs")
    args = parser.parse_args()

    if not FILTERS.is_file():
        print(f"ERROR: missing {FILTERS}", file=sys.stderr)
        return 1

    data = json.loads(FILTERS.read_text(encoding="utf-8"))
    presets = data.setdefault("presets", {})
    if args.preset not in presets:
        presets[args.preset] = {"label": args.preset, "filter_url": ""}

    url = args.url.strip()
    if not url.startswith("http"):
        print("ERROR: URL must start with http", file=sys.stderr)
        return 2

    presets[args.preset]["filter_url"] = url
    FILTERS.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"OK — saved {args.preset} filter_url ({len(url)} chars)")
    print(f"File: {FILTERS}")

    missing = [
        name
        for name in PRESETS
        if not str((presets.get(name) or {}).get("filter_url") or "").strip()
    ]
    if missing:
        print(f"Still need URLs for: {', '.join(missing)}")
    else:
        print("All presets configured — run: bash scripts/scout_on_hub.sh run --preset middle_core")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
