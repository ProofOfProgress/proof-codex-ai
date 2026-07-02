#!/usr/bin/env python3
"""Owner helper: paste a Kalodata filter URL into kalodata_filters.json."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILTERS = ROOT / "data" / "tiktok_shop" / "kalodata_filters.json"

def _preset_choices() -> list[str]:
    from shorts_bot.tiktok_shop import kalodata_filters

    names = kalodata_filters.list_preset_names()
    # include legacy aliases
    aliases = list(kalodata_filters.PRESET_ALIASES.keys())
    return sorted(set(names) | set(aliases))


def main() -> int:
    parser = argparse.ArgumentParser(description="Save Kalodata filter URL for a scout preset")
    parser.add_argument("preset", choices=_preset_choices(), help="Which course filter preset")
    parser.add_argument("url", help="Full browser URL after Apply in Kalodata")
    parser.add_argument("--list", action="store_true", help="Show which presets still need URLs")
    args = parser.parse_args()

    if not FILTERS.is_file():
        print(f"ERROR: missing {FILTERS}", file=sys.stderr)
        return 1

    from shorts_bot.tiktok_shop import kalodata_filters

    data = json.loads(FILTERS.read_text(encoding="utf-8"))
    presets = data.setdefault("presets", {})
    preset_key = kalodata_filters.normalize_preset(args.preset)
    if preset_key not in presets:
        presets[preset_key] = {"label": preset_key, "filter_url": ""}

    url = args.url.strip()
    if not url.startswith("http"):
        print("ERROR: URL must start with http", file=sys.stderr)
        return 2

    presets[preset_key]["filter_url"] = url
    FILTERS.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"OK — saved {preset_key} filter_url ({len(url)} chars)")
    print(f"File: {FILTERS}")

    missing = kalodata_filters.missing_presets(priority_only=True)
    if missing:
        print(f"Still need URLs for: {', '.join(missing)}")
    else:
        print("All presets configured — run: bash scripts/scout_on_hub.sh run --preset middle_core")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
