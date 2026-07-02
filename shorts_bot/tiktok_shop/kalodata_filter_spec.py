"""Kalodata product-list filter specs — course methods + coach high-ticket overlay."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class FilterSpec:
    """Expected state on kalodata.com/product (LIST page — never product detail)."""

    method: str
    category: str = ""
    date_range: str = "last_7_days"  # yesterday | last_7_days
    revenue_growth_min_pct: float | None = None
    creator_min: int | None = None
    creator_max: int | None = None
    commission_min_pct: float | None = None
    avg_unit_price_min: float | None = None
    revenue_min: float | None = None
    revenue_max: float | None = None
    items_sold_min: int | None = None
    items_sold_max: int | None = None
    affiliate_only: bool = False

    def with_coach_overlay(self) -> FilterSpec:
        """Coach call floor on every pick — high ticket, not 5% junk."""
        comm = self.commission_min_pct
        if comm is None or comm < 8:
            comm = 8.0
        price = self.avg_unit_price_min
        if price is None or price < 80:
            price = 80.0
        cmax = self.creator_max
        if cmax is None or cmax > 200:
            cmax = 200
        return FilterSpec(
            method=self.method,
            category=self.category,
            date_range=self.date_range,
            revenue_growth_min_pct=self.revenue_growth_min_pct,
            creator_min=self.creator_min,
            creator_max=cmax,
            commission_min_pct=comm,
            avg_unit_price_min=price,
            revenue_min=self.revenue_min,
            revenue_max=self.revenue_max,
            items_sold_min=self.items_sold_min,
            items_sold_max=self.items_sold_max,
            affiliate_only=self.affiliate_only or True,
        )


def build_spec(*, method: str, category: str = "") -> FilterSpec:
    m = method.strip().lower().replace("core_", "").replace("sauce_", "")
    base: FilterSpec
    if m == "hardcore":
        base = FilterSpec(method="hardcore", category=category, date_range="yesterday", revenue_growth_min_pct=100, creator_max=200)
    elif m == "lurkers":
        base = FilterSpec(
            method="lurkers",
            category=category,
            date_range="last_7_days",
            creator_min=10,
            creator_max=200,
            revenue_growth_min_pct=10,
            affiliate_only=True,
        )
    elif m in ("hundred_gap", "100_gap"):
        base = FilterSpec(
            method="hundred_gap",
            category=category,
            date_range="yesterday",
            revenue_min=100,
            revenue_max=1000,
            items_sold_min=50,
            items_sold_max=500,
            creator_max=250,
        )
    elif m == "middle_core":
        base = FilterSpec(
            method="middle_core",
            category=category,
            date_range="last_7_days",
            revenue_growth_min_pct=50,
            creator_max=200,
            commission_min_pct=20,
            affiliate_only=True,
        )
    elif m in ("two_hundred", "200"):
        base = FilterSpec(
            method="two_hundred",
            category=category,
            date_range="yesterday",
            revenue_growth_min_pct=100,
            creator_max=200,
        )
    else:
        raise ValueError(f"Unknown Kalodata method {method!r}")
    return base.with_coach_overlay()
