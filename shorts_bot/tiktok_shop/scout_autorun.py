"""Autonomous product scout — Kalodata/FastMoss only. Weekly drop is reference, not picks."""

from __future__ import annotations

import yaml

from shorts_bot.config import settings
from shorts_bot.tiktok_shop.product_scout import (
    ScoutProduct,
    save_products,
    scout_products,
)
from shorts_bot.tiktok_shop.scout_provider import resolve_scout_provider, scout_setup_hint


def _load_rules() -> dict:
    path = settings.data_dir / "tiktok_shop" / "momentum_scout_rules.yaml"
    if not path.is_file():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def apply_high_ticket_filters(products: list[ScoutProduct], *, limit: int = 10) -> list[ScoutProduct]:
    """Coach call 2026-06-30: price >$80, creators ≤200, commission ≥8%."""
    rules = _load_rules()
    coach = rules.get("coach_call_2026_06_30") or {}
    price_min = float(coach.get("price_min_usd") or 80)
    creator_max = int(coach.get("creators_max") or 200)
    comm_min = float(coach.get("commission_min_pct") or 8) / 100.0

    out: list[ScoutProduct] = []
    for p in products:
        if p.price < price_min:
            continue
        if p.creators > creator_max:
            continue
        if p.commission_rate < comm_min and p.commission_usd < (price_min * comm_min):
            continue
        out.append(p)
    out.sort(key=lambda x: (x.commission_usd, x.price), reverse=True)
    return out[:limit]


def run_autonomous_scout(*, preset: str = "furniture_high_ticket", limit: int = 10) -> list[ScoutProduct]:
    """Kalodata / FastMoss / hub_ui — never weekly drop."""
    provider = resolve_scout_provider(preset=preset)
    if not provider:
        # try middle_core preset as fallback URL
        provider = resolve_scout_provider(preset="middle_core")
    if not provider:
        raise RuntimeError(
            scout_setup_hint(preset=preset)
            + "\n\nWeekly Drop is disabled for picks. Wire Kalodata on hub:\n"
            "  1. Edge → kalodata.com → Furniture category + coach filters\n"
            "  2. Paste list filter URL in kalodata_filters.json\n"
            "  3. Re-run scout_autorun"
        )
    raw = scout_products(preset=preset if provider == "hub_ui" else "middle_core", limit=limit * 3)
    filtered = apply_high_ticket_filters(raw, limit=limit)
    if filtered:
        return filtered
    return raw[:limit]


def write_scout_report(products: list[ScoutProduct]) -> Path:
    from shorts_bot.tiktok_shop.scout_report import format_scout_report

    out = settings.data_dir / "tiktok_shop" / "scout_report.txt"
    rows = [p.to_dict() for p in products]
    body = format_scout_report(rows, preset="kalodata_high_ticket")
    out.write_text(body + "\n", encoding="utf-8")
    return out


def main() -> int:
    products = run_autonomous_scout(limit=10)
    save_products(products)
    report = write_scout_report(products)
    print(f"OK {len(products)} products → products.json · report {report}")
    for p in products[:5]:
        print(
            f"  · {p.product_name[:45]} | product ${p.price:.0f} | "
            f"YOU earn ${p.commission_usd:.2f}/sale | creators={p.creators}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
