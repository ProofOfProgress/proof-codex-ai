"""Google Trends — related queries + interest direction for deep research."""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from shorts_bot.config import settings

_LAST_CALL = 0.0
_MIN_INTERVAL_SEC = 2.5


@dataclass
class TrendQuery:
    query: str
    value: int


@dataclass
class GoogleTrendsResult:
    topic: str
    related_top: list[TrendQuery] = field(default_factory=list)
    related_rising: list[TrendQuery] = field(default_factory=list)
    interest_trend: str = ""
    geo: str = "US"
    property: str = "youtube"
    message: str = ""

    def context_block(self, *, max_chars: int = 1800) -> str:
        if not self.related_top and not self.related_rising and not self.interest_trend:
            return ""
        lines = [
            f"GOOGLE TRENDS ({self.property}, {self.geo}, last 3 months):",
        ]
        if self.interest_trend:
            lines.append(f"Interest direction: {self.interest_trend}")
        if self.related_top:
            lines.append("Top related queries:")
            for q in self.related_top[:10]:
                lines.append(f"- {q.query} (relative interest {q.value})")
        if self.related_rising:
            lines.append("Rising queries:")
            for q in self.related_rising[:8]:
                lines.append(f"- {q.query} (breakout {q.value})")
        if self.message:
            lines.append(f"Note: {self.message}")
        return "\n".join(lines)[:max_chars]

    def to_insights(self) -> list[dict]:
        out: list[dict] = []
        for q in self.related_top:
            out.append({"keyword": q.query, "volume": str(q.value), "competition": "", "score": "trends_top"})
        for q in self.related_rising:
            out.append({"keyword": q.query, "volume": str(q.value), "competition": "", "score": "trends_rising"})
        return out


def _rate_limit() -> None:
    global _LAST_CALL
    elapsed = time.time() - _LAST_CALL
    if elapsed < _MIN_INTERVAL_SEC:
        time.sleep(_MIN_INTERVAL_SEC - elapsed)
    _LAST_CALL = time.time()


def _df_to_queries(df) -> list[TrendQuery]:
    if df is None or df.empty:
        return []
    out: list[TrendQuery] = []
    for _, row in df.iterrows():
        query = str(row.get("query", "")).strip()
        if not query:
            continue
        try:
            value = int(row.get("value", 0))
        except (TypeError, ValueError):
            value = 0
        out.append(TrendQuery(query=query, value=value))
    return out


def _interest_direction(pytrends, keyword: str) -> str:
    """Best-effort rising/falling label; skips on rate limit."""
    try:
        iot = pytrends.interest_over_time()
    except Exception as exc:
        if "429" in str(exc):
            return "rate-limited (skipped)"
        return ""
    if iot is None or iot.empty or keyword not in iot.columns:
        return ""
    series = iot[keyword].dropna()
    if len(series) < 4:
        return ""
    first_half = series.iloc[: len(series) // 2].mean()
    second_half = series.iloc[len(series) // 2 :].mean()
    if first_half <= 0:
        return "emerging" if second_half > 0 else "low volume"
    change = (second_half - first_half) / first_half
    if change > 0.15:
        return f"rising (~{int(change * 100)}% vs prior weeks)"
    if change < -0.15:
        return f"cooling (~{int(abs(change) * 100)}% vs prior weeks)"
    return "stable"


def fetch_google_trends(topic: str) -> GoogleTrendsResult | None:
    """Pull YouTube-search Google Trends related queries for a topic."""
    if not settings.google_trends_enabled:
        return None

    geo = (settings.google_trends_geo or "US").strip() or "US"
    gprop = (settings.google_trends_gprop or "youtube").strip() or "youtube"

    try:
        from pytrends.request import TrendReq
    except ImportError:
        return GoogleTrendsResult(
            topic=topic,
            message="pytrends not installed — pip install pytrends",
        )

    _rate_limit()
    try:
        pytrends = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        pytrends.build_payload(
            [topic],
            timeframe=settings.google_trends_timeframe,
            geo=geo,
            gprop=gprop,
        )
        related = pytrends.related_queries()
    except Exception as exc:
        return GoogleTrendsResult(topic=topic, geo=geo, property=gprop, message=str(exc)[:200])

    bucket = related.get(topic) or {}
    top = _df_to_queries(bucket.get("top"))
    rising = _df_to_queries(bucket.get("rising"))

    interest = ""
    if top or rising:
        _rate_limit()
        interest = _interest_direction(pytrends, topic)

    if not top and not rising:
        # Retry shorter seed keyword (first 3 words)
        seed = " ".join(topic.split()[:3]).strip()
        if seed and seed.lower() != topic.lower():
            _rate_limit()
            try:
                pytrends.build_payload(
                    [seed],
                    timeframe=settings.google_trends_timeframe,
                    geo=geo,
                    gprop=gprop,
                )
                related2 = pytrends.related_queries()
                bucket2 = related2.get(seed) or {}
                top = _df_to_queries(bucket2.get("top"))
                rising = _df_to_queries(bucket2.get("rising"))
                if top or rising:
                    interest = interest or f"expanded seed: {seed}"
            except Exception:
                pass

    return GoogleTrendsResult(
        topic=topic,
        related_top=top,
        related_rising=rising,
        interest_trend=interest,
        geo=geo,
        property=gprop,
        message="" if (top or rising) else "Low volume on YouTube Trends — niche topic",
    )
