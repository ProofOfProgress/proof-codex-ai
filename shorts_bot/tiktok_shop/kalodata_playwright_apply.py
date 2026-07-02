"""Kalodata product-list filters via Playwright DOM — no coordinate clicks, no Gemini vision."""

from __future__ import annotations

import json
import logging
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from shorts_bot.config import settings
from shorts_bot.tiktok_shop import kalodata_filters
from shorts_bot.tiktok_shop.kalodata_filter_spec import FilterSpec, build_spec
from shorts_bot.tiktok_shop.kalodata_filter_verify import (
    PRODUCT_LIST_URL_SUFFIX,
    ParsedKalodataUi,
    VerifyResult,
    parse_ui_from_dom,
    verify_before_submit,
)
from shorts_bot.tiktok_shop.kalodata_hub_scout import (
    _capture_from_page,
    _row_to_scout,
    extract_products_from_json,
)
from shorts_bot.tiktok_shop.product_scout import ScoutProduct, save_products

logger = logging.getLogger(__name__)

LIST_URL = "https://www.kalodata.com/product"


def _profile_dir() -> Path:
    return settings.browser_profile_dir / "kalodata"


@dataclass
class ApplyResult:
    ok: bool
    message: str
    verify: VerifyResult | None = None
    filter_url: str = ""
    products: list[ScoutProduct] | None = None


def _launch_page(*, headless: bool | None = None):
    from playwright.sync_api import Page, sync_playwright

    from shorts_bot.browser.stealth import launch_stealth_context

    use_headless = settings.browser_headless if headless is None else headless
    profile = _profile_dir()
    profile.mkdir(parents=True, exist_ok=True)
    pw = sync_playwright().start()
    ctx = launch_stealth_context(pw, headless=use_headless, profile_dir=profile)
    page: Page = ctx.pages[0] if ctx.pages else ctx.new_page()
    return pw, ctx, page


def _logged_in(page) -> bool:
    body = (page.inner_text("body") or "").lower()
    if "log in" in body or "sign in" in body:
        if "product" in page.url.lower() and "kalodata" in page.url.lower():
            # Logged-in product page still shows nav; check table presence
            if page.get_by_text("All Products", exact=False).count():
                return True
        return "password" in body or "email" in body
    return True


def ensure_product_list(page) -> None:
    """Navigate to list page only — never closes browser tabs."""
    url = page.url.lower()
    if "/product/detail" in url or "/category/" in url:
        page.goto(LIST_URL, wait_until="domcontentloaded", timeout=120_000)
    elif PRODUCT_LIST_URL_SUFFIX not in url or "/detail" in url:
        page.goto(LIST_URL, wait_until="domcontentloaded", timeout=120_000)
    time.sleep(2)


def _click_first(page, *texts: str, exact: bool = False) -> bool:
    for text in texts:
        loc = page.get_by_text(text, exact=exact)
        if loc.count():
            loc.first.click(timeout=8_000)
            return True
    return False


def _click_reset(page) -> None:
    for sel in (
        'button:has-text("Reset")',
        'span:has-text("Reset")',
        '[role="button"]:has-text("Reset")',
    ):
        if page.locator(sel).count():
            page.locator(sel).first.click(timeout=5_000)
            time.sleep(0.6)
            return
    _click_first(page, "Reset filters", "Reset", exact=False)


def _row_for_label(page, label: str):
    patterns = (label, label.replace(" ", ""))
    for pat in patterns:
        loc = page.get_by_text(pat, exact=False)
        if loc.count():
            return loc.first.locator("xpath=ancestor::*[self::div or self::li or self::section][position()<=4]").last
    return page.locator("body")


def _fill_min_in_row(row, value: str | int) -> None:
    for sel in ('input[type="number"]', 'input[inputmode="numeric"]', "input"):
        inputs = row.locator(sel)
        if inputs.count():
            inp = inputs.first
            inp.click(timeout=3_000)
            inp.fill("")
            inp.fill(str(value))
            return


def _enable_row_checkbox(row) -> None:
    for sel in ('input[type="checkbox"]', '[role="checkbox"]', ".ant-checkbox", "label"):
        if row.locator(sel).count():
            row.locator(sel).first.click(timeout=3_000)
            return


def _set_date_range(page, date_range: str) -> None:
    row = _row_for_label(page, "Dates")
    row.click(timeout=3_000)
    time.sleep(0.3)
    if date_range == "yesterday":
        _click_first(page, "Yesterday", exact=False)
    else:
        _click_first(page, "Last 7 days", "Last 7 Days", exact=False)


def _set_category(page, category: str) -> None:
    if not category:
        return
    row = _row_for_label(page, "Category")
    _enable_row_checkbox(row)
    for sel in ("input", '[role="combobox"]'):
        if row.locator(sel).count():
            row.locator(sel).first.click(timeout=3_000)
            row.locator(sel).first.fill(category)
            time.sleep(0.5)
            page.get_by_text(category, exact=False).first.click(timeout=5_000)
            return
    _click_first(page, "Category", exact=False)
    page.keyboard.type(category)
    time.sleep(0.4)
    page.keyboard.press("Enter")


def _set_min_filter(page, label: str, value: float | int) -> None:
    row = _row_for_label(page, label)
    _enable_row_checkbox(row)
    _fill_min_in_row(row, int(value) if float(value).is_integer() else value)


def _set_max_filter(page, label: str, value: float | int) -> None:
    row = _row_for_label(page, label)
    _enable_row_checkbox(row)
    inputs = row.locator('input[type="number"], input')
    if inputs.count() >= 2:
        inputs.nth(1).click(timeout=3_000)
        inputs.nth(1).fill(str(int(value)))
    else:
        _fill_min_in_row(row, value)


def _set_revenue_range(page, spec: FilterSpec) -> None:
    if spec.revenue_min is None and spec.revenue_max is None:
        return
    row = _row_for_label(page, "Revenue")
    _enable_row_checkbox(row)
    if spec.revenue_min is not None:
        _fill_min_in_row(row, int(spec.revenue_min))
    if spec.revenue_max is not None:
        inputs = row.locator('input[type="number"], input')
        if inputs.count() >= 2:
            inputs.nth(1).fill(str(int(spec.revenue_max)))


def _set_items_sold_range(page, spec: FilterSpec) -> None:
    if spec.items_sold_min is None and spec.items_sold_max is None:
        return
    row = _row_for_label(page, "Item Sold")
    if not row.count():
        row = _row_for_label(page, "Items Sold")
    _enable_row_checkbox(row)
    if spec.items_sold_min is not None:
        _fill_min_in_row(row, spec.items_sold_min)
    if spec.items_sold_max is not None:
        inputs = row.locator('input[type="number"], input')
        if inputs.count() >= 2:
            inputs.nth(1).fill(str(spec.items_sold_max))


def _set_affiliate_only(page) -> None:
    for label in ("Is Affiliate Product", "Affiliate Product", "Affiliate"):
        row = _row_for_label(page, label)
        if row.count() and row.inner_text(timeout=1_000):
            _enable_row_checkbox(row)
            _click_first(page, "Yes", exact=False)
            return


def apply_spec_to_page(page, spec: FilterSpec) -> None:
    """Apply course filter spec on product LIST page via DOM."""
    ensure_product_list(page)
    _click_reset(page)
    time.sleep(0.5)

    _set_date_range(page, spec.date_range)

    if spec.category:
        _set_category(page, spec.category)

    _set_revenue_range(page, spec)

    if spec.revenue_growth_min_pct is not None:
        _set_min_filter(page, "Revenue Growth", spec.revenue_growth_min_pct)

    if spec.creator_min is not None:
        _set_min_filter(page, "Creator", spec.creator_min)
    if spec.creator_max is not None:
        _set_max_filter(page, "Creator", spec.creator_max)

    if spec.avg_unit_price_min is not None:
        _set_min_filter(page, "Avg Unit Price", spec.avg_unit_price_min)
        _set_min_filter(page, "Unit Price", spec.avg_unit_price_min)

    if spec.commission_min_pct is not None:
        _set_min_filter(page, "Commission", spec.commission_min_pct)

    _set_items_sold_range(page, spec)

    if spec.affiliate_only:
        _set_affiliate_only(page)


def _click_submit(page) -> None:
    for sel in (
        'button:has-text("Submit")',
        'button:has-text("Apply")',
        'span:has-text("Submit")',
    ):
        if page.locator(sel).count():
            page.locator(sel).first.click(timeout=8_000)
            time.sleep(2)
            return
    _click_first(page, "Submit", "Apply", exact=False)
    time.sleep(2)


def _input_values_in_row(row) -> list[str]:
    vals: list[str] = []
    for sel in ('input[type="number"]', 'input[type="text"]', "input"):
        loc = row.locator(sel)
        for i in range(min(loc.count(), 4)):
            try:
                v = loc.nth(i).input_value(timeout=1_000).strip()
                if v:
                    vals.append(v)
            except Exception:
                continue
    return vals


def read_ui_from_page(page) -> ParsedKalodataUi:
    ensure_product_list(page)
    sidebar = ""
    for sel in ("aside", '[class*="filter"]', '[class*="sidebar"]'):
        loc = page.locator(sel)
        if loc.count():
            try:
                sidebar = loc.first.inner_text(timeout=3_000)
                if len(sidebar) > 80:
                    break
            except Exception:
                continue
    pills: list[str] = []
    for sel in ('[class*="pill"]', '[class*="tag"]', '[class*="filtering"]'):
        loc = page.locator(sel)
        for i in range(min(loc.count(), 20)):
            try:
                t = loc.nth(i).inner_text(timeout=1_000).strip()
                if t and len(t) < 80:
                    pills.append(t)
            except Exception:
                continue
    body = page.inner_text("body") or ""
    ui = parse_ui_from_dom(url=page.url, sidebar_text=sidebar, body_text=body, filtering_pills=pills)

    growth_vals = _input_values_in_row(_row_for_label(page, "Revenue Growth"))
    if growth_vals and ui.revenue_growth_min_pct is None:
        ui = ParsedKalodataUi(**{**ui.__dict__, "revenue_growth_min_pct": float(growth_vals[0])})

    comm_vals = _input_values_in_row(_row_for_label(page, "Commission"))
    if comm_vals and ui.commission_min_pct is None:
        ui = ParsedKalodataUi(**{**ui.__dict__, "commission_min_pct": float(comm_vals[0])})

    creator_vals = _input_values_in_row(_row_for_label(page, "Creator"))
    if creator_vals:
        patch: dict[str, Any] = {}
        if ui.creator_min is None and len(creator_vals) >= 1:
            patch["creator_min"] = int(float(creator_vals[0]))
        if ui.creator_max is None and len(creator_vals) >= 2:
            patch["creator_max"] = int(float(creator_vals[1]))
        elif ui.creator_max is None and len(creator_vals) == 1:
            patch["creator_max"] = int(float(creator_vals[0]))
        if patch:
            ui = ParsedKalodataUi(**{**ui.__dict__, **patch})

    price_vals = _input_values_in_row(_row_for_label(page, "Avg Unit Price"))
    if not price_vals:
        price_vals = _input_values_in_row(_row_for_label(page, "Unit Price"))
    if price_vals and ui.avg_unit_price_min is None:
        ui = ParsedKalodataUi(**{**ui.__dict__, "avg_unit_price_min": float(price_vals[0])})

    rev_vals = _input_values_in_row(_row_for_label(page, "Revenue"))
    if rev_vals:
        patch = {}
        if ui.revenue_min is None:
            patch["revenue_min"] = float(rev_vals[0])
        if ui.revenue_max is None and len(rev_vals) >= 2:
            patch["revenue_max"] = float(rev_vals[1])
        if patch:
            ui = ParsedKalodataUi(**{**ui.__dict__, **patch})

    return ui


def _save_filter_url(method: str, url: str) -> None:
    if not url or "/detail" in url.lower():
        return
    key = kalodata_filters.normalize_preset(method)
    block = kalodata_filters.preset_block(key) or kalodata_filters.preset_block(method)
    data = kalodata_filters.load_config()
    presets = data.setdefault("presets", {})
    presets[key] = {**(block or {}), "filter_url": url}
    kalodata_filters.filters_path().write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _scroll_product_table(page, *, rounds: int = 4) -> None:
    for _ in range(rounds):
        page.mouse.wheel(0, 900)
        time.sleep(0.6)


def pick_products_from_list(
    page,
    *,
    preset: str,
    limit: int = 10,
    min_commission_pct: float = 8.0,
    max_creators: int = 200,
    min_price: float = 80.0,
) -> list[ScoutProduct]:
    """Scroll list, capture API rows, rank by commission + coach gates."""
    _scroll_product_table(page)
    rows = _capture_from_page(page, wait_s=4.0)
    scored: list[ScoutProduct] = []
    for row in rows:
        item = _row_to_scout(row, preset=preset)
        if not item:
            continue
        comm_pct = item.commission_rate * 100 if item.commission_rate <= 1 else item.commission_rate
        if item.price < min_price:
            continue
        if item.creators > max_creators:
            continue
        if comm_pct < min_commission_pct and item.commission_usd < (min_price * min_commission_pct / 100):
            continue
        scored.append(item)
    scored.sort(key=lambda p: (p.commission_usd, p.gmv_period, p.score), reverse=True)
    if not scored and rows:
        for row in rows[:limit]:
            item = _row_to_scout(row, preset=preset)
            if item:
                scored.append(item)
    return scored[:limit]


def run_verified_apply(
    *,
    method: str,
    category: str = "",
    headless: bool | None = None,
    save_url: bool = True,
    scout_limit: int = 0,
) -> ApplyResult:
    """
    Playwright path: list page → reset → apply spec → DOM verify → submit.
    Never closes Edge or uses desktop-helper coordinates.
    """
    if not settings.browser_enabled:
        return ApplyResult(ok=False, message="BROWSER_ENABLED=false — enable Playwright on hub")

    spec = build_spec(method=method, category=category)
    pw, ctx, page = _launch_page(headless=headless)
    products: list[ScoutProduct] | None = None
    try:
        page.goto(LIST_URL, wait_until="domcontentloaded", timeout=120_000)
        time.sleep(2)
        if not _logged_in(page):
            return ApplyResult(
                ok=False,
                message=(
                    "Kalodata not logged in (Playwright profile). On hub run once:\n"
                    "  python3 -m shorts_bot.browser.cli open kalodata --minutes 10"
                ),
            )

        ensure_product_list(page)
        pre = read_ui_from_page(page)
        if pre.page_type == "product_detail":
            ensure_product_list(page)
            pre = read_ui_from_page(page)

        apply_spec_to_page(page, spec)
        time.sleep(0.8)
        ui = read_ui_from_page(page)
        verify = verify_before_submit(spec, ui, phase="preflight")
        if not verify.ok:
            full = verify_before_submit(spec, ui)
            verify = full if not full.ok else verify
        if not verify.ok:
            return ApplyResult(
                ok=False,
                message="ABORTED — Submit NOT pressed (DOM verify failed)",
                verify=verify,
            )

        _click_submit(page)
        time.sleep(2)
        filter_url = page.url
        post = read_ui_from_page(page)
        post_verify = verify_before_submit(spec, post)

        if save_url and filter_url and PRODUCT_LIST_URL_SUFFIX in filter_url.lower():
            if "/detail" not in filter_url.lower():
                _save_filter_url(method, filter_url)

        if scout_limit > 0:
            products = pick_products_from_list(page, preset=method, limit=scout_limit)
            if products:
                save_products(products)

        ok = post_verify.ok or bool(filter_url)
        msg = f"Filters applied via Playwright: {method}" + (f" + {category}" if category else "")
        if not post_verify.ok:
            msg += " (soft pass — check filtering pills)"
        return ApplyResult(ok=ok, message=msg, verify=post_verify, filter_url=filter_url, products=products)
    finally:
        ctx.close()
        pw.stop()


def main() -> int:
    import argparse

    logging.basicConfig(level=logging.INFO)
    p = argparse.ArgumentParser(description="Kalodata filters via Playwright DOM (hub)")
    p.add_argument("--method", required=True)
    p.add_argument("--category", default="Furniture")
    p.add_argument("--scout-limit", type=int, default=0, help="Save top N products after apply")
    p.add_argument("--visible", action="store_true", help="Show browser window")
    args = p.parse_args()
    res = run_verified_apply(
        method=args.method,
        category=args.category,
        headless=False if args.visible else None,
        scout_limit=args.scout_limit,
    )
    print(res.message)
    if res.filter_url:
        print(f"URL: {res.filter_url[:160]}")
    if res.verify and res.verify.issues:
        for issue in res.verify.issues:
            print(f"  - {issue}")
    if res.products:
        print(f"Products saved: {len(res.products)}")
        for p in res.products[:5]:
            print(f"  · {p.product_name[:50]} ${p.price:.0f} comm=${p.commission_usd:.2f}")
    return 0 if res.ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
