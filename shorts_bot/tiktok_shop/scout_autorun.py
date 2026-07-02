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
    """Coach call gates + per-product quality validation."""
    from shorts_bot.tiktok_shop.scout_product_quality import filter_quality_products

    passed, rejected = filter_quality_products(products, limit=limit, strict=True)
    if rejected:
        for p, q in rejected[:5]:
            print(f"REJECT {p.product_name[:40]}: {'; '.join(q.issues)}", flush=True)
    return passed


def run_multi_preset_scout(*, limit: int = 10) -> list[ScoutProduct]:
    """Run every P0 preset with a saved filter_url; merge + dedupe + coach filters."""
    from shorts_bot.tiktok_shop import kalodata_filters
    from shorts_bot.tiktok_shop.product_scout import scout_products

    keys = kalodata_filters.launch_priority_presets()
    merged: dict[str, ScoutProduct] = {}
    for key in keys:
        if not kalodata_filters.preset_has_url(key):
            continue
        try:
            rows = scout_products(preset=key, limit=limit)
        except Exception as exc:
            print(f"WARN scout {key}: {exc}", flush=True)
            continue
        for p in rows:
            k = p.product_id or p.product_name.lower()
            prev = merged.get(k)
            if not prev or p.score > prev.score:
                merged[k] = p

    products = list(merged.values())
    products.sort(key=lambda x: (x.commission_usd, x.score), reverse=True)
    filtered = apply_high_ticket_filters(products, limit=limit)
    return filtered if filtered else products[:limit]


def run_kalopilot_multi_scout(*, limit: int = 10, category: str = "Furniture") -> list[ScoutProduct]:
    """Run every course method via KaloPilot API — no browser, owner-free."""
    from shorts_bot.tiktok_shop import kalodata_client
    from shorts_bot.tiktok_shop.kalodata_pilot_queries import launch_method_presets
    from shorts_bot.tiktok_shop.kalodata_scout import scout_via_kalodata

    if not kalodata_client.configured():
        return []

    merged: dict[str, ScoutProduct] = {}
    for method in launch_method_presets():
        try:
            rows = scout_via_kalodata(preset=method, limit=limit)
        except Exception as exc:
            print(f"WARN KaloPilot {method}: {exc}", flush=True)
            continue
        for p in rows:
            k = p.product_id or p.product_name.lower()
            prev = merged.get(k)
            if not prev or p.score > prev.score:
                merged[k] = p

    products = list(merged.values())
    products.sort(key=lambda x: (x.commission_usd, x.score), reverse=True)
    filtered = apply_high_ticket_filters(products, limit=limit)
    return filtered if filtered else products[:limit]


def run_autonomous_scout(*, preset: str = "coach_high_ticket_furniture", limit: int = 10) -> list[ScoutProduct]:
    """Kalodata KaloPilot → Edge CDP → hub URLs — never weekly drop."""
    from shorts_bot.tiktok_shop import kalodata_client, kalodata_filters

    if kalodata_client.configured():
        multi = run_kalopilot_multi_scout(limit=limit)
        if multi:
            return multi

    if kalodata_filters.hub_ui_ready():
        multi = run_multi_preset_scout(limit=limit)
        if multi:
            return multi

    if settings.has_gemini:
        try:
            from shorts_bot.tiktok_shop.kalodata_live_scrape import scout_live_edge_table

            live = scout_live_edge_table(limit=limit)
            if live:
                return live
        except Exception as exc:
            print(f"WARN live Kalodata scrape: {exc}", flush=True)

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
    from shorts_bot.tiktok_shop.scout_product_quality import (
        filter_quality_products,
        format_quality_report,
    )
    from shorts_bot.tiktok_shop.scout_report import format_scout_report

    out = settings.data_dir / "tiktok_shop" / "scout_report.txt"
    quality_path = settings.data_dir / "tiktok_shop" / "scout_quality_report.txt"
    passed, rejected = filter_quality_products(products, limit=20, strict=True)
    quality_path.write_text(format_quality_report(passed, rejected), encoding="utf-8")

    rows = [p.to_dict() for p in products]
    body = format_scout_report(rows, preset="kalodata_high_ticket")
    body += f"\n\nQuality detail: {quality_path}\n"
    out.write_text(body + "\n", encoding="utf-8")
    return out


def main() -> int:
    products = run_autonomous_scout(limit=10)
    if not products:
        raise SystemExit(
            "Scout returned 0 quality products — check Kalodata backend "
            "(KALODATA_PILOT_TOKEN or hub filter URLs). See docs/FOR_OWNER_HANDS_OFF_SCOUT.md"
        )
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
