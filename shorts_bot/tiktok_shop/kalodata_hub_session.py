"""Hub Kalodata UI session — verified filter apply (no blind misclicks)."""

from __future__ import annotations

import json
import logging
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.tiktok_shop.kalodata_filter_spec import FilterSpec, build_spec
from shorts_bot.tiktok_shop.kalodata_filter_verify import (
    PRODUCT_LIST_URL_SUFFIX,
    ParsedKalodataUi,
    VerifyResult,
    gemini_vision_prompt,
    parse_ui_json,
    safe_click,
    verify_before_submit,
)

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
LIST_URL = "https://www.kalodata.com/product"
SHOT = "data/desktop_hub/kalodata_session.png"

# Calibrated for 1920×1080 — LEFT SIDEBAR ONLY (x ≤ 380).
COORDS = {
    "reset": (130, 726),
    "submit": (275, 726),
    "dates_field": (280, 133),
    "date_last_7": (280, 210),
    "date_yesterday": (280, 185),
    "category_field": (280, 195),
    "sidebar_focus": (200, 400),
    "growth_checkbox": (150, 318),
    "growth_min_field": (300, 318),
    "creator_checkbox": (150, 530),
    "creator_max_field": (300, 530),
    "price_checkbox": (150, 575),
    "price_min_field": (280, 575),
    "commission_checkbox": (150, 650),
    "commission_min_field": (280, 650),
    "revenue_checkbox": (150, 268),
    "revenue_min_field": (280, 268),
    "revenue_max_field": (340, 268),
}


@dataclass
class SessionResult:
    ok: bool
    message: str
    verify: VerifyResult | None = None
    filter_url: str = ""


def _hub(command: str) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, "-m", "shorts_bot.hub_remote", "run", "--", command]
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)


def _dh(*args: str) -> None:
    if args and args[0] == "click" and len(args) >= 3:
        safe_click(int(args[1]), int(args[2]))
    _hub("cd ~/proof-codex-ai && python3 -m shorts_bot.desktop_hub.cli " + " ".join(args))
    time.sleep(0.35)


def _pull_screenshot(local: Path) -> Path:
    _hub(f"cd ~/proof-codex-ai && python3 -m shorts_bot.desktop_hub.cli screenshot --out {SHOT}")
    proc = _hub(
        f"cd ~/proof-codex-ai && python3 -c \"import base64; print(base64.b64encode(open('{SHOT}','rb').read()).decode())\""
    )
    m = re.search(r"([A-Za-z0-9+/]{200,}={0,2})", proc.stdout or "")
    if not m:
        raise RuntimeError("Could not pull hub screenshot")
    raw = m.group(1)
    pad = (-len(raw)) % 4
    local.parent.mkdir(parents=True, exist_ok=True)
    local.write_bytes(__import__("base64").b64decode(raw + "=" * pad))
    return local


def _read_ui(local: Path) -> ParsedKalodataUi:
    key = (settings.gemini_api_key or "").strip()
    if not key:
        raise RuntimeError("GEMINI_API_KEY required to verify Kalodata UI — aborting instead of misclicking")
    from google import genai

    client = genai.Client(api_key=key)
    model = (settings.gemini_model or "gemini-2.5-flash-lite").strip()
    last_err: Exception | None = None
    for attempt in range(4):
        try:
            resp = client.models.generate_content(
                model=model,
                contents=[
                    gemini_vision_prompt(),
                    genai.types.Part.from_bytes(data=local.read_bytes(), mime_type="image/png"),
                ],
            )
            raw = (resp.text or "").strip()
            if raw.startswith("```"):
                raw = re.sub(r"^```(?:json)?\s*", "", raw)
                raw = re.sub(r"\s*```$", "", raw)
            return parse_ui_json(json.loads(raw))
        except Exception as exc:
            last_err = exc
            if "503" in str(exc):
                time.sleep(5 * (attempt + 1))
                continue
            break
    raise RuntimeError(f"Kalodata UI vision failed — NOT clicking blindly: {last_err}")


def ensure_product_list_page() -> None:
    """Close detail rabbit-hole — fresh product list tab."""
    _dh("press", "esc")
    _dh("hotkey", "ctrl", "l")
    _dh("type", LIST_URL)
    _dh("press", "enter")
    time.sleep(3)


def close_duplicate_tabs(max_close: int = 6) -> None:
    for _ in range(max_close):
        _dh("hotkey", "ctrl", "w")
        time.sleep(0.25)
    ensure_product_list_page()


def _apply_spec(spec: FilterSpec) -> None:
    """Apply filters on LIST page — sidebar coords only."""
    _dh("click", str(COORDS["sidebar_focus"][0]), str(COORDS["sidebar_focus"][1]))
    _dh("click", str(COORDS["reset"][0]), str(COORDS["reset"][1]))
    time.sleep(0.6)

    _dh("click", str(COORDS["dates_field"][0]), str(COORDS["dates_field"][1]))
    time.sleep(0.4)
    if spec.date_range == "yesterday":
        _dh("click", str(COORDS["date_yesterday"][0]), str(COORDS["date_yesterday"][1]))
    else:
        _dh("click", str(COORDS["date_last_7"][0]), str(COORDS["date_last_7"][1]))
    time.sleep(0.4)

    if spec.category:
        _dh("click", str(COORDS["category_field"][0]), str(COORDS["category_field"][1]))
        _dh("type", spec.category)
        _dh("press", "enter")
        time.sleep(0.4)

    if spec.revenue_min is not None or spec.revenue_max is not None:
        _dh("click", str(COORDS["revenue_checkbox"][0]), str(COORDS["revenue_checkbox"][1]))
        if spec.revenue_min is not None:
            _dh("click", str(COORDS["revenue_min_field"][0]), str(COORDS["revenue_min_field"][1]))
            _dh("type", str(int(spec.revenue_min)))
        if spec.revenue_max is not None:
            _dh("click", str(COORDS["revenue_max_field"][0]), str(COORDS["revenue_max_field"][1]))
            _dh("type", str(int(spec.revenue_max)))

    if spec.revenue_growth_min_pct is not None:
        _dh("click", str(COORDS["sidebar_focus"][0]), str(COORDS["sidebar_focus"][1]))
        for _ in range(2):
            _dh("press", "pagedown")
        _dh("click", str(COORDS["growth_checkbox"][0]), str(COORDS["growth_checkbox"][1]))
        _dh("click", str(COORDS["growth_min_field"][0]), str(COORDS["growth_min_field"][1]))
        _dh("type", str(int(spec.revenue_growth_min_pct)))

    if spec.creator_max is not None or spec.creator_min is not None:
        _dh("click", str(COORDS["creator_checkbox"][0]), str(COORDS["creator_checkbox"][1]))
        _dh("click", str(COORDS["creator_max_field"][0]), str(COORDS["creator_max_field"][1]))
        _dh("type", str(spec.creator_max or 200))

    if spec.avg_unit_price_min is not None:
        _dh("click", str(COORDS["price_checkbox"][0]), str(COORDS["price_checkbox"][1]))
        _dh("click", str(COORDS["price_min_field"][0]), str(COORDS["price_min_field"][1]))
        _dh("type", str(int(spec.avg_unit_price_min)))

    if spec.commission_min_pct is not None:
        _dh("click", str(COORDS["commission_checkbox"][0]), str(COORDS["commission_checkbox"][1]))
        _dh("click", str(COORDS["commission_min_field"][0]), str(COORDS["commission_min_field"][1]))
        _dh("type", str(int(spec.commission_min_pct)))


def _capture_filter_url() -> str:
    _dh("hotkey", "alt", "tab")
    time.sleep(0.3)
    _dh("hotkey", "ctrl", "l")
    time.sleep(0.2)
    _dh("hotkey", "ctrl", "c")
    time.sleep(0.4)
    proc = _hub("powershell.exe -NoProfile -Command (Get-Clipboard).Trim()")
    for ln in reversed((proc.stdout or "").splitlines()):
        ln = ln.strip()
        if ln.startswith("http") and "kalodata" in ln.lower() and PRODUCT_LIST_URL_SUFFIX in ln.lower():
            if "/detail" not in ln.lower():
                return ln
    return ""


def run_verified_session(
    *,
    method: str,
    category: str = "",
    close_tabs: bool = True,
    max_attempts: int = 2,
) -> SessionResult:
    """
    Full gate: list page → reset → apply → VERIFY → submit (only if verify passes).
  Misclick protection: abort if vision fails or verify fails.
    """
    spec = build_spec(method=method, category=category)
    local = settings.data_dir / "desktop_hub" / "kalodata_session.png"

    if close_tabs:
        close_duplicate_tabs()

    last_verify: VerifyResult | None = None
    for attempt in range(max_attempts):
        ensure_product_list_page()
        shot = _pull_screenshot(local)
        try:
            pre = _read_ui(shot)
        except RuntimeError as exc:
            return SessionResult(
                ok=False,
                message=f"ABORTED before any filter clicks (misclick protection): {exc}",
            )
        if pre.page_type != "product_list":
            if close_tabs:
                close_duplicate_tabs()
            last_verify = VerifyResult(
                ok=False,
                issues=(f"Pre-flight: on {pre.page_type!r}, need product_list — not clicking filters.",),
            )
            continue

        _apply_spec(spec)
        time.sleep(0.8)
        shot = _pull_screenshot(local)
        try:
            ui = _read_ui(shot)
        except RuntimeError as exc:
            return SessionResult(
                ok=False,
                message=f"ABORTED after apply — Submit NOT pressed: {exc}",
                verify=last_verify,
            )
        last_verify = verify_before_submit(spec, ui)
        if last_verify.ok:
            _dh("click", str(COORDS["submit"][0]), str(COORDS["submit"][1]))
            time.sleep(2)
            shot2 = _pull_screenshot(local)
            ui2 = _read_ui(shot2)
            post = verify_before_submit(spec, ui2)
            url = _capture_filter_url()
            if post.ok or url:
                return SessionResult(
                    ok=True,
                    message=f"Filters applied: {method}" + (f" + {category}" if category else ""),
                    verify=post,
                    filter_url=url,
                )
            return SessionResult(
                ok=True,
                message="Submitted — post-verify soft pass (check filtering pills)",
                verify=post,
                filter_url=url,
            )
        logger.warning("Kalodata verify failed attempt %s: %s", attempt + 1, last_verify.issues)

    issues = "; ".join(last_verify.issues) if last_verify else "unknown"
    return SessionResult(
        ok=False,
        message=f"ABORTED — filters NOT submitted (misclick protection). Issues: {issues}",
        verify=last_verify,
    )


def main() -> int:
    import argparse

    logging.basicConfig(level=logging.INFO)
    p = argparse.ArgumentParser(description="Verified Kalodata filter apply on hub")
    p.add_argument("--method", required=True, help="hardcore|lurkers|hundred_gap|middle_core|two_hundred")
    p.add_argument("--category", default="Furniture")
    p.add_argument("--cleanup-tabs", action="store_true", help="Close stray tabs first")
    args = p.parse_args()
    res = run_verified_session(
        method=args.method,
        category=args.category,
        close_tabs=args.cleanup_tabs,
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
