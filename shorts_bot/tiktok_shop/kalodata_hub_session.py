"""Hub Kalodata UI session — Playwright DOM primary; legacy desktop helper deprecated."""

from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass
from shorts_bot.tiktok_shop.kalodata_filter_verify import VerifyResult
from shorts_bot.tiktok_shop.kalodata_playwright_apply import run_verified_apply

logger = logging.getLogger(__name__)


@dataclass
class SessionResult:
    ok: bool
    message: str
    verify: VerifyResult | None = None
    filter_url: str = ""


def run_verified_session(
    *,
    method: str,
    category: str = "",
    close_tabs: bool = False,
    max_attempts: int = 2,
    scout_limit: int = 0,
    legacy_desktop: bool = False,
) -> SessionResult:
    """
    Apply course filters on Kalodata product LIST page.

    Default: Playwright DOM (kalodata browser profile). Never closes Edge tabs.
    `--legacy-desktop` uses deprecated coordinate helper (do not use at launch).
    """
    if legacy_desktop:
        return _run_legacy_desktop(
            method=method,
            category=category,
            close_tabs=close_tabs,
            max_attempts=max_attempts,
        )

    if close_tabs:
        logger.info(
            "close_tabs ignored — Playwright navigates to list URL only; Edge tabs untouched"
        )

    last: SessionResult | None = None
    for attempt in range(max_attempts):
        res = run_verified_apply(
            method=method,
            category=category,
            scout_limit=scout_limit,
        )
        last = SessionResult(
            ok=res.ok,
            message=res.message,
            verify=res.verify,
            filter_url=res.filter_url,
        )
        if res.ok:
            return last
        logger.warning("Playwright apply attempt %s failed: %s", attempt + 1, res.message)

    return last or SessionResult(ok=False, message="Kalodata apply failed")


def _run_legacy_desktop(
    *,
    method: str,
    category: str,
    close_tabs: bool,
    max_attempts: int,
) -> SessionResult:
    """Deprecated coordinate path — kept for emergency fallback only."""
    from shorts_bot.tiktok_shop import kalodata_hub_session_legacy as legacy

    return legacy.run_verified_session(
        method=method,
        category=category,
        close_tabs=close_tabs,
        max_attempts=max_attempts,
    )


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO)
    p = argparse.ArgumentParser(description="Verified Kalodata filter apply on hub (Playwright)")
    p.add_argument("--method", required=True, help="hardcore|lurkers|hundred_gap|middle_core|two_hundred")
    p.add_argument("--category", default="Furniture")
    p.add_argument(
        "--cleanup-tabs",
        action="store_true",
        help="No-op with Playwright (safe). Legacy desktop only.",
    )
    p.add_argument("--scout-limit", type=int, default=0, help="Save top N products after filters")
    p.add_argument("--legacy-desktop", action="store_true", help="DANGEROUS: coordinate clicks")
    p.add_argument("--visible", action="store_true", help="Show Playwright browser")
    args = p.parse_args(argv)

    if args.legacy_desktop and args.cleanup_tabs:
        logger.warning("--cleanup-tabs with legacy desktop can close Edge — avoid at launch")

    if args.visible and not args.legacy_desktop:
        import os

        os.environ["BROWSER_HEADLESS"] = "false"

    res = run_verified_session(
        method=args.method,
        category=args.category,
        close_tabs=args.cleanup_tabs,
        scout_limit=args.scout_limit,
        legacy_desktop=args.legacy_desktop,
    )
    print(res.message)
    if res.filter_url:
        print(f"URL: {res.filter_url[:120]}")
    if res.verify and res.verify.issues:
        for issue in res.verify.issues:
            print(f"  - {issue}")
    return 0 if res.ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
