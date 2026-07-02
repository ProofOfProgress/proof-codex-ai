#!/usr/bin/env python3
"""Hub: screenshot live Kalodata table → quality-gated products.json."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shorts_bot.tiktok_shop.kalodata_live_scrape import scout_live_edge_table
from shorts_bot.tiktok_shop.product_scout import save_products
from shorts_bot.tiktok_shop.scout_product_quality import filter_quality_products, format_quality_report


def main() -> int:
    products = scout_live_edge_table(limit=15)
    print(f"live_count={len(products)}")
    if not products:
        from shorts_bot.tiktok_shop.kalodata_live_scrape import gemini_extract_products, hub_screenshot, rows_to_scout
        from shorts_bot.tiktok_shop.scout_product_quality import validate_product

        shot = hub_screenshot()
        rows = gemini_extract_products(shot, limit=15)
        print(f"gemini_rows={len(rows)}")
        raw = rows_to_scout(rows)
        print(f"parsed={len(raw)}")
        for p in raw[:5]:
            q = validate_product(p)
            print(f"  {p.product_name[:40]} GMV={p.gmv_period:.0f} comm={p.commission_rate} -> {q.issues}")
    for p in products[:8]:
        comm = p.commission_rate * 100 if p.commission_rate <= 1 else p.commission_rate
        print(
            f"  {p.product_name[:48]} | ${p.price:.0f} | {comm:.0f}% | "
            f"GMV ${p.gmv_period:,.0f} | cr {p.creators}"
        )
    if not products:
        return 2
    save_products(products)
    passed, rejected = filter_quality_products(products, limit=20)
    report = ROOT / "data" / "tiktok_shop" / "scout_quality_report.txt"
    report.write_text(format_quality_report(passed, rejected), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
