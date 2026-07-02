"""Coach-quality gates for scout picks — reject junk before products.json."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from shorts_bot.config import settings
from shorts_bot.tiktok_shop.product_scout import ScoutProduct

BANNED_PRESET_PARTS = ("weekly_drop", "momentum_weekly", "hub_live_scrape", "discord")


@dataclass(frozen=True)
class ProductQuality:
    ok: bool
    issues: tuple[str, ...]
    tier: str  # pass | warn | reject


def _coach_rules() -> dict:
    path = settings.data_dir / "tiktok_shop" / "momentum_scout_rules.yaml"
    if not path.is_file():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data.get("coach_call_2026_06_30") or {}


def _commission_pct(p: ScoutProduct) -> float:
    r = float(p.commission_rate or 0)
    return r * 100 if r <= 1 else r


def validate_product(p: ScoutProduct, *, strict: bool = True) -> ProductQuality:
    """
    Per-product coach gate (2026-06-30) + launch sanity.
    strict=True enforces $10k GMV; strict=False allows $3k+ for hundred_gap/yesterday presets.
    """
    coach = _coach_rules()
    price_min = float(coach.get("price_min_usd") or 80)
    creator_max = int(coach.get("creators_max") or 200)
    comm_min = float(coach.get("commission_min_pct") or 8)
    gmv_min = float(coach.get("revenue_7d_min_usd") or 10_000)

    preset = (p.preset or "").lower()
    issues: list[str] = []

    if any(b in preset for b in BANNED_PRESET_PARTS):
        issues.append(f"banned source preset {p.preset!r} — use Kalodata scout only")

    if not (p.product_name or "").strip():
        issues.append("missing product name")

    if p.price < price_min:
        issues.append(f"price ${p.price:.0f} < ${price_min:.0f} coach floor")

    comm = _commission_pct(p)
    if comm < comm_min:
        issues.append(f"commission {comm:.1f}% < {comm_min:.0f}% (Ovios-style junk)")

    if p.creators > creator_max:
        issues.append(f"creators {p.creators} > {creator_max} (saturated)")

    gmv_floor = 3_000 if preset in ("two_hundred", "hundred_gap", "sauce_hundred_gap") else gmv_min
    if strict and p.gmv_period < gmv_floor:
        issues.append(f"period GMV ${p.gmv_period:,.0f} < ${gmv_floor:,.0f}")

    if comm < 12 and p.creators > 150 and p.gmv_period > 50_000:
        issues.append("high revenue + many creators + low commission — bad pick")

    if p.videos == 0 and p.gmv_period < gmv_min and strict:
        issues.append("no affiliate videos and low GMV")

    if issues:
        return ProductQuality(ok=False, issues=tuple(issues), tier="reject")
    warns: list[str] = []
    if p.gmv_period < gmv_min:
        warns.append(f"GMV ${p.gmv_period:,.0f} below ideal ${gmv_min:,.0f} (acceptable for yesterday presets)")
    if not (p.product_id or "").strip():
        warns.append("missing product_id — add before upload")
    if warns:
        return ProductQuality(ok=True, issues=tuple(warns), tier="warn")
    return ProductQuality(ok=True, issues=(), tier="pass")


def filter_quality_products(
    products: list[ScoutProduct],
    *,
    limit: int = 10,
    strict: bool = True,
    allow_warn: bool = True,
) -> tuple[list[ScoutProduct], list[tuple[ScoutProduct, ProductQuality]]]:
    """Return passing products + rejected list for owner report."""
    passed: list[ScoutProduct] = []
    rejected: list[tuple[ScoutProduct, ProductQuality]] = []

    ranked = sorted(
        products,
        key=lambda x: (x.commission_usd, x.gmv_period, x.score),
        reverse=True,
    )
    for p in ranked:
        q = validate_product(p, strict=strict)
        if q.ok and (q.tier == "pass" or (allow_warn and q.tier == "warn")):
            passed.append(p)
        else:
            rejected.append((p, q))
        if len(passed) >= limit:
            break
    return passed, rejected


def format_quality_report(
    passed: list[ScoutProduct],
    rejected: list[tuple[ScoutProduct, ProductQuality]],
) -> str:
    lines = [
        f"Scout quality gate — {len(passed)} pass, {len(rejected)} rejected",
        "",
    ]
    if passed:
        lines.append("## PASS")
        for p in passed:
            comm = _commission_pct(p)
            lines.append(
                f"- {p.product_name[:55]} | ${p.price:.0f} | {comm:.0f}% comm "
                f"| ${p.commission_usd:.2f}/sale | GMV ${p.gmv_period:,.0f} | "
                f"creators {p.creators} | preset {p.preset}"
            )
    if rejected:
        lines.append("")
        lines.append("## REJECTED")
        for p, q in rejected[:15]:
            lines.append(f"- {p.product_name[:50]} — {'; '.join(q.issues)}")
    return "\n".join(lines) + "\n"
