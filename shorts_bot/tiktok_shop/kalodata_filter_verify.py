"""Verify Kalodata UI state before Submit — blocks misclicks on product detail etc."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from shorts_bot.tiktok_shop.kalodata_filter_spec import FilterSpec

# Product LIST page only — clicks for filters must stay in left sidebar (1920×1080 hub).
SIDEBAR_CLICK_X_MAX = 380
PRODUCT_LIST_URL_SUFFIX = "/product"
FORBIDDEN_URL_PARTS = ("/product/detail", "/category/detail", "/category?")


@dataclass
class ParsedKalodataUi:
    page_type: str = "unknown"  # product_list | product_detail | category | other
    url_hint: str = ""
    date_range: str = ""
    category: str = ""
    revenue_min: float | None = None
    revenue_max: float | None = None
    revenue_growth_min_pct: float | None = None
    creator_min: int | None = None
    creator_max: int | None = None
    commission_min_pct: float | None = None
    avg_unit_price_min: float | None = None
    items_sold_min: int | None = None
    items_sold_max: int | None = None
    filtering_pills: list[str] = field(default_factory=list)
    submit_enabled: bool | None = None
    duplicate_product_tabs: int = 0
    raw_notes: str = ""


def parse_ui_json(data: dict[str, Any]) -> ParsedKalodataUi:
    pills = data.get("filtering_pills") or data.get("active_filters") or []
    if not isinstance(pills, list):
        pills = []
    return ParsedKalodataUi(
        page_type=str(data.get("page_type") or "unknown").lower(),
        url_hint=str(data.get("url_hint") or ""),
        date_range=str(data.get("date_range") or "").lower(),
        category=str(data.get("category") or ""),
        revenue_min=_num(data.get("revenue_min")),
        revenue_max=_num(data.get("revenue_max")),
        revenue_growth_min_pct=_num(data.get("revenue_growth_min_pct")),
        creator_min=_int(data.get("creator_min")),
        creator_max=_int(data.get("creator_max")),
        commission_min_pct=_num(data.get("commission_min_pct")),
        avg_unit_price_min=_num(data.get("avg_unit_price_min")),
        items_sold_min=_int(data.get("items_sold_min")),
        items_sold_max=_int(data.get("items_sold_max")),
        filtering_pills=[str(p) for p in pills],
        submit_enabled=data.get("submit_enabled") if isinstance(data.get("submit_enabled"), bool) else None,
        duplicate_product_tabs=_int(data.get("duplicate_product_tabs")) or 0,
        raw_notes=str(data.get("notes") or ""),
    )


def _num(raw: Any) -> float | None:
    if raw is None:
        return None
    try:
        return float(str(raw).replace("%", "").replace(",", "").strip())
    except ValueError:
        return None


def _int(raw: Any) -> int | None:
    n = _num(raw)
    return int(n) if n is not None else None


def _page_type_from_url(url: str) -> str:
    lower = (url or "").lower()
    if "/product/detail" in lower:
        return "product_detail"
    if "/category/" in lower:
        return "category"
    if "/product" in lower:
        return "product_list"
    return "other"


def _extract_num_near_label(text: str, labels: tuple[str, ...]) -> float | None:
    lower = text.lower()
    for label in labels:
        idx = lower.find(label.lower())
        if idx < 0:
            continue
        chunk = text[idx : idx + 120]
        m = re.search(r"(\d+(?:\.\d+)?)\s*%?", chunk)
        if m:
            return float(m.group(1))
    return None


def _extract_int_pair(text: str, labels: tuple[str, ...]) -> tuple[int | None, int | None]:
    lower = text.lower()
    for label in labels:
        idx = lower.find(label.lower())
        if idx < 0:
            continue
        after = text[idx + len(label) : idx + len(label) + 80]
        line_chunk = "\n".join(after.strip().split("\n")[:2])
        nums = [int(float(x)) for x in re.findall(r"(\d+(?:\.\d+)?)", line_chunk)[:4]]
        if len(nums) >= 2:
            return nums[0], nums[1]
        if len(nums) == 1:
            return nums[0], None
    return None, None


def parse_ui_from_dom(
    *,
    url: str,
    sidebar_text: str = "",
    body_text: str = "",
    filtering_pills: list[str] | None = None,
) -> ParsedKalodataUi:
    """Parse Kalodata filter state from Playwright DOM text — no screenshot vision."""
    pills = list(filtering_pills or [])
    combined = f"{sidebar_text}\n{body_text}\n" + " ".join(pills)
    lower = combined.lower()

    date_range = ""
    if "yesterday" in lower:
        date_range = "yesterday"
    elif "last 7" in lower or "7 day" in lower:
        date_range = "last 7 days"
    elif "last 30" in lower or "30 day" in lower:
        date_range = "last 30 days"

    category = ""
    for pill in pills:
        if "category" in pill.lower():
            category = pill.split(":", 1)[-1].strip()
            break
    if not category:
        m = re.search(r"category[:\s]+([A-Za-z][A-Za-z &]+)", combined, re.I)
        if m:
            category = m.group(1).strip()

    growth = _extract_num_near_label(combined, ("Revenue Growth", "Growth Rate", "growth"))
    comm = _extract_num_near_label(combined, ("Commission", "commission"))
    price = _extract_num_near_label(combined, ("Avg Unit Price", "Unit Price", "avg price"))
    rev_min, rev_max = _extract_int_pair(sidebar_text or combined, ("Revenue", "revenue"))
    cr_min, cr_max = _extract_int_pair(sidebar_text or combined, ("Creator Number", "Creators", "Creator"))
    if cr_min is not None and cr_max is None:
        cr_max, cr_min = cr_min, None
    sold_min, sold_max = _extract_int_pair(sidebar_text or combined, ("Item Sold", "Items Sold"))

    submit_enabled: bool | None = None
    if re.search(r"\bsubmit\b", lower):
        submit_enabled = "disabled" not in lower or "submit" in sidebar_text.lower()

    return ParsedKalodataUi(
        page_type=_page_type_from_url(url),
        url_hint=url,
        date_range=date_range,
        category=category,
        revenue_min=float(rev_min) if rev_min is not None else None,
        revenue_max=float(rev_max) if rev_max is not None else None,
        revenue_growth_min_pct=growth,
        creator_min=cr_min,
        creator_max=cr_max,
        commission_min_pct=comm,
        avg_unit_price_min=price,
        items_sold_min=sold_min,
        items_sold_max=sold_max,
        filtering_pills=pills,
        submit_enabled=submit_enabled,
        duplicate_product_tabs=0,
        raw_notes="dom",
    )


def _date_ok(actual: str, expected: str) -> bool:
    a = actual.lower()
    e = expected.lower()
    if e == "yesterday":
        return "yesterday" in a
    if e == "last_7_days":
        return "7" in a and "day" in a
    return e in a


@dataclass(frozen=True)
class VerifyResult:
    ok: bool
    issues: tuple[str, ...] = ()


def verify_before_submit(spec: FilterSpec, ui: ParsedKalodataUi, *, phase: str = "full") -> VerifyResult:
    """Verify Kalodata UI. phase=preflight checks page + dates only (pre-submit DOM)."""
    issues: list[str] = []

    if ui.page_type != "product_list":
        issues.append(
            f"WRONG PAGE: {ui.page_type!r} — filters belong on Product LIST (/product), "
            "not product detail. Close detail tabs and open kalodata.com/product."
        )

    for bad in FORBIDDEN_URL_PARTS:
        if bad in (ui.url_hint or "").lower():
            issues.append(f"URL is detail/category page ({bad}) — go to product list.")

    if "last 30" in ui.date_range or "30 day" in ui.date_range:
        if spec.date_range in ("yesterday", "last_7_days"):
            issues.append(f"Dates still Last 30 Days — need {spec.date_range}.")

    if spec.date_range and ui.date_range and not _date_ok(ui.date_range, spec.date_range):
        issues.append(f"Date range mismatch: saw {ui.date_range!r}, need {spec.date_range!r}.")

    if phase == "preflight":
        return VerifyResult(ok=not issues, issues=tuple(issues))

    if spec.category:
        cat = spec.category.lower()
        pill_text = " ".join(ui.filtering_pills).lower()
        if cat not in (ui.category or "").lower() and cat not in pill_text:
            issues.append(f"Category {spec.category!r} not applied.")

    if spec.revenue_growth_min_pct is not None:
        g = ui.revenue_growth_min_pct
        if g is None:
            issues.append(f"Revenue growth min not set — need ≥{spec.revenue_growth_min_pct:g}%.")
        elif g < spec.revenue_growth_min_pct:
            issues.append(f"Revenue growth min {g:g}% < required {spec.revenue_growth_min_pct:g}%.")
        elif g == 0:
            issues.append("Revenue growth >0% only — useless filter; set course minimum.")

    if spec.creator_max is not None:
        c = ui.creator_max
        if c is None:
            issues.append(f"Creator max not set — need ≤{spec.creator_max}.")
        elif c > spec.creator_max:
            issues.append(f"Creator max {c} > {spec.creator_max}.")

    if spec.commission_min_pct is not None:
        comm = ui.commission_min_pct
        if comm is None:
            issues.append(f"Commission min not set — need ≥{spec.commission_min_pct:g}%.")
        elif comm < spec.commission_min_pct:
            issues.append(f"Commission min {comm:g}% < {spec.commission_min_pct:g}%.")

    if spec.avg_unit_price_min is not None:
        p = ui.avg_unit_price_min
        if p is None:
            issues.append(f"Avg unit price min not set — need ≥${spec.avg_unit_price_min:g}.")
        elif p < spec.avg_unit_price_min:
            issues.append(f"Avg unit price min ${p:g} < ${spec.avg_unit_price_min:g}.")

    if spec.revenue_min is not None:
        if ui.revenue_min is None or ui.revenue_min < spec.revenue_min:
            issues.append(f"Revenue min need ≥{spec.revenue_min:g}.")

    if spec.revenue_max is not None:
        if ui.revenue_max is None or ui.revenue_max > spec.revenue_max:
            issues.append(f"Revenue max need ≤{spec.revenue_max:g}.")

    if ui.duplicate_product_tabs > 2:
        issues.append(f"Too many Kalodata product tabs ({ui.duplicate_product_tabs}) — close duplicates.")

    if ui.submit_enabled is False:
        issues.append("Submit button disabled — filters incomplete or wrong page.")

    return VerifyResult(ok=not issues, issues=tuple(issues))


def gemini_vision_prompt() -> str:
    return """Analyze this Kalodata screenshot. Return ONLY valid JSON (no markdown):
{
  "page_type": "product_list|product_detail|category|other",
  "url_hint": "from address bar if visible",
  "date_range": "e.g. Last 7 Days or Last 30 Days",
  "category": "selected category or empty",
  "revenue_min": number or null,
  "revenue_max": number or null,
  "revenue_growth_min_pct": number or null,
  "creator_min": number or null,
  "creator_max": number or null,
  "commission_min_pct": number or null,
  "avg_unit_price_min": number or null,
  "items_sold_min": number or null,
  "items_sold_max": number or null,
  "filtering_pills": ["Dates: ...", "Category: ..."],
  "submit_enabled": true/false/null,
  "duplicate_product_tabs": number of browser tabs showing same product detail,
  "notes": "short"
}
product_list = All Products table with left filter sidebar. product_detail = single product metrics page."""


def safe_click(x: int, y: int) -> None:
    if x > SIDEBAR_CLICK_X_MAX:
        raise ValueError(
            f"Refusing misclick at ({x},{y}) — filter clicks must be in left sidebar (x≤{SIDEBAR_CLICK_X_MAX}). "
            "You are probably on product detail or the results table."
        )
