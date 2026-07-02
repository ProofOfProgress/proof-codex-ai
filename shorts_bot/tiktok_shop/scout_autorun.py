"""Autonomous product scout — course intel first, APIs when wired."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from shorts_bot.config import settings
from shorts_bot.tiktok_shop.product_scout import (
    ScoutProduct,
    load_momentum_weekly_drop,
    save_products,
    scout_products,
)
from shorts_bot.tiktok_shop.scout_provider import resolve_scout_provider, scout_setup_hint


def _load_rules() -> dict:
    path = settings.data_dir / "tiktok_shop" / "momentum_scout_rules.yaml"
    if not path.is_file():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def filter_weekly_drop(products: list[ScoutProduct], *, limit: int = 10) -> list[ScoutProduct]:
    """Apply coach rules — weekly drop is hints, not gospel."""
    rules = _load_rules()
    coach = rules.get("coach_call_2026_06_30") or {}
    formula = rules.get("scout_formula") or {}
    creator_max = int(coach.get("creators_max") or 200)
    comm_min = float(formula.get("commission_min_pct") or 10) / 100.0
    price_min = float(formula.get("price_min_usd") or 12)
    growth_min = float(coach.get("growth_min_pct") or 30)

    out: list[ScoutProduct] = []
    for p in products:
        if p.creators > creator_max:
            continue
        if p.commission_rate < comm_min and p.commission_usd < 5:
            continue
        if p.price < price_min:
            continue
        # weekly_revenue in gmv_period is in thousands from parser — use growth from score proxy
        out.append(p)
    out.sort(key=lambda x: (x.commission_usd, x.score), reverse=True)
    return out[:limit]


def run_autonomous_scout(*, preset: str = "middle_core", limit: int = 10) -> list[ScoutProduct]:
    """Best available backend; weekly drop filtered by course rules."""
    provider = resolve_scout_provider(preset=preset)
    if provider == "momentum_weekly_drop":
        products = filter_weekly_drop(load_momentum_weekly_drop(limit=50), limit=limit)
        if products:
            return products
    if provider:
        try:
            return scout_products(preset=preset, limit=limit)
        except RuntimeError:
            pass
    products = filter_weekly_drop(load_momentum_weekly_drop(limit=50), limit=limit)
    if products:
        return products
    raise RuntimeError(scout_setup_hint(preset=preset))


def write_scout_report(products: list[ScoutProduct]) -> Path:
    from shorts_bot.tiktok_shop.scout_report import format_scout_report

    out = settings.data_dir / "tiktok_shop" / "scout_report.txt"
    rows = [p.to_dict() for p in products]
    body = format_scout_report(rows, preset="autonomous")
    out.write_text(body + "\n", encoding="utf-8")
    return out


def main() -> int:
    products = run_autonomous_scout(limit=10)
    save_products(products)
    report = write_scout_report(products)
    print(f"OK {len(products)} products → products.json · report {report}")
    for p in products[:5]:
        print(f"  · {p.product_name[:50]} ${p.commission_usd}/sale creators={p.creators}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
