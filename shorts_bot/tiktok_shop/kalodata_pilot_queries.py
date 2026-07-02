"""KaloPilot natural-language queries — course methods + coach overlay (no browser)."""

from __future__ import annotations

from shorts_bot.config import settings
from shorts_bot.tiktok_shop.kalodata_filter_spec import FilterSpec, build_spec

_METHOD_ALIASES: dict[str, str] = {
    "core_middle_core": "middle_core",
    "core_two_hundred": "two_hundred",
    "sauce_hardcore": "hardcore",
    "sauce_lurkers": "lurkers",
    "sauce_hundred_gap": "hundred_gap",
    "coach_high_ticket_furniture": "middle_core",
    "coach_high_ticket_all": "middle_core",
}


def normalize_method(preset: str) -> str:
    key = (preset or "middle_core").strip().lower()
    return _METHOD_ALIASES.get(key, key.replace("core_", "").replace("sauce_", ""))


def _date_phrase(spec: FilterSpec) -> str:
    if spec.date_range == "yesterday":
        return "Yesterday (1 day)"
    return "Last 7 days"


def build_pilot_query(
    *,
    preset: str = "middle_core",
    category: str = "",
    limit: int = 10,
) -> str:
    """
    Course-aligned KaloPilot query — mirrors kalodata_filter_spec.build_spec().
    Owner-free: cloud/hub calls API directly.
    """
    method = normalize_method(preset)
    spec = build_spec(method=method, category=category or "")
    region = (settings.kalodata_region or "US").strip()
    lines = [
        f"{region} TikTok Shop affiliate product research using Kalodata data.",
        f"Course method: {method}. Date range: {_date_phrase(spec)}.",
        f"Return up to {limit} products matching ALL filters where possible:",
    ]
    if spec.category:
        lines.append(f"- Category: {spec.category}")
    if spec.revenue_growth_min_pct is not None:
        lines.append(f"- Revenue growth at least {spec.revenue_growth_min_pct:g}%")
    if spec.revenue_min is not None:
        rev = f"- Revenue at least ${spec.revenue_min:g}"
        if spec.revenue_max is not None:
            rev += f" and at most ${spec.revenue_max:g}"
        lines.append(rev)
    if spec.items_sold_min is not None:
        sold = f"- Items sold at least {spec.items_sold_min}"
        if spec.items_sold_max is not None:
            sold += f", at most {spec.items_sold_max}"
        lines.append(sold)
    if spec.creator_min is not None:
        lines.append(f"- Creator count at least {spec.creator_min}")
    if spec.creator_max is not None:
        lines.append(f"- Creator count at most {spec.creator_max}")
    if spec.commission_min_pct is not None:
        lines.append(f"- Affiliate commission at least {spec.commission_min_pct:g}%")
    if spec.avg_unit_price_min is not None:
        lines.append(f"- Average unit price at least ${spec.avg_unit_price_min:g}")
    if spec.affiliate_only:
        lines.append("- Affiliate / TikTok Shop affiliate product only (not brand-only listings)")
    lines.extend(
        [
            "- Prefer video-driven revenue (not live-only)",
            "- Reject saturated junk: skip very low commission (~5%) with 150+ creators unless GMV exceptional",
            "- Prefer products with room for new affiliates (not peaked / declining)",
            "",
            "Return a markdown table with columns exactly:",
            "product_name | product_id | price_usd | commission_pct | gmv_usd | creators | videos | trend | cover_url",
            "Use real Kalodata data only. product_id = TikTok Shop numeric ID if known.",
        ]
    )
    return "\n".join(lines)


def launch_method_presets() -> list[str]:
    return ["middle_core", "hardcore", "lurkers", "hundred_gap", "two_hundred"]
