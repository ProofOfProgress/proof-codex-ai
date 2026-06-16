"""Facebook Page insights via Graph API (when token has pages_read_engagement)."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from dataclasses import dataclass

from shorts_bot.integrations.facebook_credentials import resolve_facebook_credentials

GRAPH = "https://graph.facebook.com/v21.0"


@dataclass
class FacebookInsightsSummary:
    page_name: str
    followers: int | None
    impressions_7d: int | None
    message: str


def fetch_page_insights(*, days: int = 7) -> FacebookInsightsSummary:
    pid, token, _ = resolve_facebook_credentials()
    if not pid or not token:
        return FacebookInsightsSummary("", None, None, "No Facebook API token")

    name = pid
    followers = None
    impressions = None

    try:
        url = f"{GRAPH}/{pid}?fields=name,followers_count,fan_count&access_token={urllib.parse.quote(token)}"
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = json.loads(resp.read().decode())
        name = str(data.get("name") or pid)
        followers = data.get("followers_count") or data.get("fan_count")
    except Exception as exc:
        return FacebookInsightsSummary(name, None, None, f"Page info failed: {exc}")

    since = __import__("datetime").datetime.utcnow() - __import__("datetime").timedelta(days=days)
    since_ts = int(since.timestamp())
    metrics = "page_impressions,page_post_engagements"
    insight_url = (
        f"{GRAPH}/{pid}/insights?metric={metrics}"
        f"&period=day&since={since_ts}&access_token={urllib.parse.quote(token)}"
    )
    try:
        with urllib.request.urlopen(insight_url, timeout=30) as resp:
            ins = json.loads(resp.read().decode())
        for row in ins.get("data") or []:
            if row.get("name") == "page_impressions":
                values = row.get("values") or []
                impressions = sum(int(v.get("value") or 0) for v in values)
    except Exception as exc:
        return FacebookInsightsSummary(
            name,
            int(followers) if followers is not None else None,
            None,
            f"Insights need pages_read_engagement: {exc}",
        )

    return FacebookInsightsSummary(
        name,
        int(followers) if followers is not None else None,
        impressions,
        "OK",
    )


def probe_facebook_analytics() -> tuple[bool, str]:
    summary = fetch_page_insights()
    if summary.message != "OK":
        return False, summary.message
    parts = [f"{summary.page_name}"]
    if summary.followers is not None:
        parts.append(f"{summary.followers} followers")
    if summary.impressions_7d is not None:
        parts.append(f"{summary.impressions_7d} impressions (7d)")
    return True, " — ".join(parts)
