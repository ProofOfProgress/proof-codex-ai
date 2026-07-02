"""Resolve product scout backend — Kalodata or FastMoss only."""

from __future__ import annotations

from shorts_bot.config import settings
from shorts_bot.tiktok_shop import fastmoss_client, kalodata_client


def resolve_scout_provider() -> str:
    """Return 'kalodata', 'fastmoss', or '' if none configured."""
    choice = (settings.scout_provider or "auto").strip().lower()
    if choice == "kalodata":
        return "kalodata" if kalodata_client.configured() else ""
    if choice == "fastmoss":
        return "fastmoss" if fastmoss_client.configured() else ""
    if kalodata_client.configured():
        return "kalodata"
    if fastmoss_client.configured():
        return "fastmoss"
    return ""


def scout_setup_hint() -> str:
    return (
        "Product scout needs **Kalodata** or **FastMoss** (pick one):\n"
        "  Kalodata: KALODATA_PILOT_TOKEN from kalodata.com/pilot → Connect OpenClaw\n"
        "  FastMoss: apply free API trial at developers.fastmoss.com/free-trial.html\n"
        "See docs/FOR_OWNER_KALODATA_OR_FASTMOSS.md"
    )
