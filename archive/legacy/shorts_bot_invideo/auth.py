"""InVideo credentials + browser session status."""

from __future__ import annotations

from shorts_bot.config import settings
from shorts_bot.invideo.mcp_client import probe_mcp


def _secret_real(value: str | None) -> bool:
    v = (value or "").strip()
    if not v:
        return False
    lower = v.lower()
    return not any(p in lower for p in ("your-", "placeholder", "paste-your", "iv_api_xxx"))


def api_key_configured() -> bool:
    return _secret_real(settings.invideo_api_key)


def credentials_status_message() -> str:
    if api_key_configured():
        return "INVIDEO_API_KEY saved — MCP + API ready"
    return "No API key yet — browser login still works for MCP projects"


def check_browser_logged_in() -> tuple[bool, str]:
    """Probe Agent One workspace — more reliable than signup redirect."""
    from shorts_bot.invideo.agent_one import probe_agent_one_session

    return probe_agent_one_session()


def auth_status() -> dict:
    mcp_ok, mcp_detail = probe_mcp(api_key=settings.invideo_api_key if api_key_configured() else None)
    browser_ok, browser_detail = check_browser_logged_in()
    return {
        "api_key_configured": api_key_configured(),
        "mcp_ready": mcp_ok,
        "mcp_detail": mcp_detail,
        "browser_logged_in": browser_ok,
        "browser_detail": browser_detail,
        "production_ready": mcp_ok and browser_ok,
        "app_url": settings.invideo_app_url,
    }


def credentials_status_message_full() -> str:
    st = auth_status()
    parts = [credentials_status_message()]
    parts.append(f"MCP: {st['mcp_detail']}")
    parts.append(f"Browser: {st['browser_detail']}")
    if st["production_ready"]:
        parts.append("Ready — agent can start InVideo projects from scripts")
    else:
        parts.append("Run: python3 -m shorts_bot.invideo.handoff_cli")
    return " · ".join(parts)
