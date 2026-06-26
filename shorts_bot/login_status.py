"""Live integration status — TikTok Shop APIs only."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any

from shorts_bot.config import settings


@dataclass
class ServiceStatus:
    id: str
    label: str
    ready: bool
    detail: str
    action: str | None = None


def _check_echotik() -> ServiceStatus:
    from shorts_bot.tiktok_shop import echotik_client

    if echotik_client.configured():
        return ServiceStatus("echotik", "EchoTik scout", True, "Credentials configured")
    return ServiceStatus(
        "echotik",
        "EchoTik scout",
        False,
        "ECHOTIK_USERNAME + ECHOTIK_PASSWORD missing",
        "docs/FOR_OWNER_ECHOTIK_SETUP.md",
    )


def _check_kling() -> ServiceStatus:
    from shorts_bot.tiktok_shop import kling_client

    if kling_client.configured():
        return ServiceStatus("kling", "Kling video API", True, "JWT or API key configured")
    return ServiceStatus(
        "kling",
        "Kling video API",
        False,
        "KLING_ACCESS_KEY + KLING_SECRET_KEY missing",
        "docs/FOR_OWNER_KLING_SETUP.md",
    )


def _check_printify() -> ServiceStatus:
    from shorts_bot.tiktok_shop import printify_client

    if not printify_client.configured():
        return ServiceStatus(
            "printify",
            "Printify API",
            False,
            "PRINTIFY_API_TOKEN missing",
            "docs/FOR_OWNER_PRINTIFY_API.md",
        )
    try:
        shops = printify_client.list_shops()
        return ServiceStatus("printify", "Printify API", True, f"{len(shops)} shop(s) connected")
    except Exception as exc:
        return ServiceStatus("printify", "Printify API", False, str(exc)[:120], "docs/FOR_OWNER_PRINTIFY_API.md")


def _check_tiktok_oauth() -> ServiceStatus:
    from shorts_bot.tiktok.oauth import auth_status, upload_ready

    st = auth_status()
    if upload_ready():
        return ServiceStatus("tiktok_oauth", "TikTok OAuth upload", True, "Content Posting API ready")
    if st.get("credentials_configured"):
        return ServiceStatus(
            "tiktok_oauth",
            "TikTok OAuth upload",
            False,
            "Run OAuth connect",
            "docs/FOR_OWNER_TIKTOK_SETUP.md",
        )
    return ServiceStatus(
        "tiktok_oauth",
        "TikTok OAuth upload",
        False,
        "TIKTOK_CLIENT_KEY + SECRET missing",
        "docs/FOR_OWNER_TIKTOK_SETUP.md",
    )


def _check_zernio() -> ServiceStatus:
    from shorts_bot.zernio.auth_cli import status_dict

    st = status_dict()
    if not st["configured"]:
        return ServiceStatus("zernio", "Zernio cross-post", False, "ZERNIO_API_KEY missing", "https://zernio.com")
    if st["tiktok_ready"]:
        return ServiceStatus("zernio", "Zernio cross-post", True, "TikTok connected")
    return ServiceStatus(
        "zernio",
        "Zernio cross-post",
        False,
        "API key OK — connect TikTok at zernio.com",
        "python3 -m shorts_bot.zernio.auth_cli status",
    )


def _check_slack() -> ServiceStatus:
    from shorts_bot.integrations.slack import has_slack_bot, has_slack_webhook

    if has_slack_bot() or has_slack_webhook():
        return ServiceStatus("slack", "Slack alerts", True, f"#{settings.slack_channel_name}")
    return ServiceStatus("slack", "Slack alerts", False, "Optional — not configured", "data/SLACK_SETUP_CHECKLIST.md")


def _check_web() -> ServiceStatus:
    return ServiceStatus("web", "Web status API", True, f"http://{settings.web_host}:{settings.web_port}")


def _check_image_api() -> ServiceStatus:
    if settings.has_replicate_images:
        return ServiceStatus("replicate", "Replicate (video gen)", True, "Token configured")
    if settings.has_fal_images:
        return ServiceStatus("fal", "Fal.ai (video gen)", True, "Key configured")
    return ServiceStatus(
        "image_api",
        "Replicate/Fal (optional)",
        False,
        "Not configured",
        "docs/CURSOR_SECRETS.md",
    )


def _check_playwright() -> ServiceStatus:
    from shorts_bot.browser.session import is_playwright_ready

    ok, detail = is_playwright_ready()
    return ServiceStatus("playwright", "Playwright browser", ok, detail)


def full_status() -> list[dict[str, Any]]:
    items = [
        _check_web(),
        _check_echotik(),
        _check_kling(),
        _check_printify(),
        _check_tiktok_oauth(),
        _check_zernio(),
        _check_slack(),
        _check_image_api(),
        _check_playwright(),
    ]
    return [asdict(s) for s in items]


def print_report() -> int:
    from rich.console import Console
    from rich.table import Table

    console = Console()
    table = Table(title="TikTok Shop — connection status")
    table.add_column("Service")
    table.add_column("Ready")
    table.add_column("Detail")
    table.add_column("If not done")

    not_ready = 0
    for row in full_status():
        ready = "✓" if row["ready"] else "—"
        if not row["ready"]:
            not_ready += 1
        table.add_row(row["label"], ready, row["detail"], row.get("action") or "")
    console.print(table)
    console.print(f"\n[bold]{len(full_status()) - not_ready}[/bold] ready, [yellow]{not_ready}[/yellow] need attention")
    return 0 if not_ready == 0 else 1


if __name__ == "__main__":
    raise SystemExit(print_report())
