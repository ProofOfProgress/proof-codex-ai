"""Resolve product scout backend — Kalodata hub UI, KaloPilot, FastMoss, or course intel."""

from __future__ import annotations

from shorts_bot.config import settings
from shorts_bot.tiktok_shop import fastmoss_client, kalodata_client, kalodata_filters


def momentum_weekly_drop_available() -> bool:
    path = settings.data_dir / "tiktok_shop" / "momentum_weekly_drop.json"
    return path.is_file() and path.stat().st_size > 10


def resolve_scout_provider(*, preset: str = "middle_core") -> str:
    """
    Return scout backend id.

    auto order (owner-free / hands-off first):
      1. kalodata — KaloPilot token (no browser, no Edge)
      2. hub_ui — saved Kalodata filter URL + hub browser
      3. fastmoss — OpenAPI keys
    Weekly drop is NEVER auto — reference only (owner 2026-07).
    """
    from shorts_bot.agent_credentials import load_agent_credentials

    load_agent_credentials()
    choice = (settings.scout_provider or "auto").strip().lower()
    if choice == "hub_ui":
        return "hub_ui" if kalodata_filters.preset_has_url(preset) else ""
    if choice == "kalodata":
        return "kalodata" if kalodata_client.configured() else ""
    if choice == "fastmoss":
        return "fastmoss" if fastmoss_client.configured() else ""
    if choice == "momentum_weekly_drop":
        return "momentum_weekly_drop" if momentum_weekly_drop_available() else ""
    if choice == "auto":
        if kalodata_client.configured():
            return "kalodata"
        if kalodata_filters.preset_has_url(preset):
            return "hub_ui"
        if fastmoss_client.configured():
            return "fastmoss"
    return ""


def scout_setup_hint(*, preset: str = "middle_core") -> str:
    missing = kalodata_filters.missing_presets()
    weekly = settings.data_dir / "tiktok_shop" / "momentum_weekly_drop.json"
    return (
        "Product scout needs a backend (pick ONE — see docs/FOR_OWNER_HANDS_OFF_SCOUT.md):\n"
        "  **Hands-off (best):** KALODATA_PILOT_TOKEN from kalodata.com/pilot → Cursor secrets → new agent\n"
        "  **Hub Edge:** KALODATA_EDGE_CDP_URL=http://127.0.0.1:9222 + Edge remote debug\n"
        f"  **Filter URLs:** paste preset {preset!r} in kalodata_filters.json "
        f"(missing: {', '.join(missing) or 'none'})\n"
        "  FastMoss: developers.fastmoss.com free API trial\n"
        f"  Course intel: run hub crawl → {weekly}\n"
    )
