#!/usr/bin/env python3
"""Parse Momentum weekly-drop crawl text into products JSON for scout reference."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def parse_weekly_drop(text: str) -> list[dict]:
    products: list[dict] = []
    blocks = re.split(r"\n(?=[A-Za-z]+\n#\d+\n)", text)
    for block in blocks:
        m_name = re.search(r"^#\d+\n(.+?)(?:\n\n|\nPRICE)", block, re.M | re.S)
        if not m_name:
            continue
        name = m_name.group(1).strip().split("\n")[0]
        def _field(label: str) -> str:
            m = re.search(rf"^{label}\n\n(.+?)(?:\n[A-Z]|\Z)", block, re.M | re.S)
            return (m.group(1).strip() if m else "")

        price_raw = _field("PRICE").replace("$", "").replace(",", "")
        comm_raw = _field("COMMISSION")
        rate_m = re.search(r"(\d+(?:\.\d+)?)\s*%", comm_raw)
        rev_raw = _field("WEEKLY REV").replace("$", "").replace("k", "000").replace(",", "")
        creators = _field("CREATORS")
        growth = _field("GROWTH").replace("+", "").replace("%", "")
        pitch = block.split("\n\n")[1] if "\n\n" in block else ""
        if m_name:
            pitch_lines = block.split("\n\n")
            pitch = pitch_lines[1] if len(pitch_lines) > 1 and not pitch_lines[1].startswith("#") else ""

        try:
            price = float(re.sub(r"[^\d.]", "", price_raw) or "0")
        except ValueError:
            price = 0.0
        try:
            rate = float(rate_m.group(1)) / 100.0 if rate_m else 0.0
        except ValueError:
            rate = 0.0
        try:
            gmv = float(re.sub(r"[^\d.]", "", rev_raw) or "0")
        except ValueError:
            gmv = 0.0
        try:
            growth_pct = float(re.sub(r"[^\d.]", "", growth) or "0")
        except ValueError:
            growth_pct = 0.0
        try:
            creator_n = int(re.sub(r"[^\d]", "", creators) or "0")
        except ValueError:
            creator_n = 0

        products.append(
            {
                "product_name": name,
                "price": price,
                "commission_rate": rate,
                "commission_usd": round(price * rate, 2),
                "weekly_revenue": gmv,
                "creators": creator_n,
                "growth_pct": growth_pct,
                "pitch": pitch[:500],
                "source": "momentum_weekly_drop",
            }
        )
    return products


def main() -> int:
    src = ROOT / "data/research/course/inbox/momentum-crawl-2026-07-01.md"
    if len(sys.argv) > 1:
        src = Path(sys.argv[1])
    if not src.is_file():
        print(f"Missing {src}", file=sys.stderr)
        return 1
    text = src.read_text(encoding="utf-8")
    # Extract weekly-drop section only
    if "weekly-drop" in text:
        part = text.split("/weekly-drop", 1)[-1]
        part = part.split("\n## ", 1)[0]
        text = part
    products = parse_weekly_drop(text)
    out = ROOT / "data/tiktok_shop/momentum_weekly_drop.json"
    out.write_text(json.dumps({"products": products, "count": len(products)}, indent=2) + "\n")
    print(f"OK {len(products)} products -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
