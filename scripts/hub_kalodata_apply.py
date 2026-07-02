#!/usr/bin/env python3
"""Hub Kalodata UI — open browser, apply preset filters via desktop helper + Gemini vision."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shorts_bot.config import settings
from shorts_bot.desktop_hub.client import DesktopHubClient, DesktopHubError
from shorts_bot.tiktok_shop import kalodata_filters

SHOT_DIR = settings.data_dir / "desktop_hub"
KALODATA_PRODUCT = "https://www.kalodata.com/product"

PRESET_STEPS: dict[str, list[str]] = {
    "middle_core": [
        "Open Kalodata product page if not already there.",
        "Set Dates to Last 7 days.",
        "Set Revenue Growth Rate to at least 50% or 'Growing' / fast-growing preset.",
        "Set Creator Number maximum to 200.",
        "Set commission filter to at least 20% if visible (or Is Affiliate Product = Yes).",
        "Click Submit / Apply at bottom of filter panel.",
    ],
    "two_hundred": [
        "Set Dates to Yesterday.",
        "Set Revenue Growth Rate to at least 100%.",
        "Set Creator Number maximum to 200.",
        "Click Submit / Apply.",
    ],
}


def _run_desktop(args: list[str]) -> None:
    subprocess.run(
        [sys.executable, "-m", "shorts_bot.desktop_hub.cli", *args],
        cwd=ROOT,
        check=True,
    )


def _screenshot(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    _run_desktop(["screenshot", "--out", str(path)])
    return path


def _open_kalodata() -> None:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "shorts_bot.hub_remote",
            "run",
            "--",
            "cmd.exe /c start msedge " + KALODATA_PRODUCT,
        ],
        cwd=ROOT,
        check=False,
    )
    time.sleep(8)


def _gemini_click_hint(image_path: Path, goal: str) -> tuple[int, int] | None:
    key = (settings.gemini_api_key or "").strip()
    if not key:
        return None
    try:
        from google import genai
    except ImportError:
        return None

    client = genai.Client(api_key=key)
    model = (settings.gemini_model or "gemini-2.5-flash-lite").strip()
    raw = image_path.read_bytes()
    prompt = (
        f"Goal: {goal}\n"
        "Return ONLY one line: CLICK x y  (pixel coordinates on this 1920x1080 screenshot). "
        "If unsure, return: SKIP"
    )
    try:
        resp = client.models.generate_content(
            model=model,
            contents=[
                prompt,
                genai.types.Part.from_bytes(data=raw, mime_type="image/png"),
            ],
        )
        text = (resp.text or "").strip()
    except Exception:
        return None
    m = re.search(r"CLICK\s+(\d+)\s+(\d+)", text, re.I)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))


def _capture_url_via_bar(client: DesktopHubClient) -> str:
    client.click(500, 52, clicks=3)
    time.sleep(0.3)
    client.hotkey("ctrl", "c")
    time.sleep(0.3)
    proc = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", "Get-Clipboard"],
        capture_output=True,
        text=True,
        check=False,
    )
    url = (proc.stdout or "").strip()
    if url.startswith("http") and "kalodata" in url:
        return url
    return ""


def apply_preset(preset: str, *, max_steps: int = 12, use_vision: bool = True) -> str:
    if preset not in PRESET_STEPS:
        raise SystemExit(f"Unknown preset {preset!r}")

    client = DesktopHubClient()
    client.ping()

    _open_kalodata()
    steps = PRESET_STEPS[preset]
    for i, step in enumerate(steps[:max_steps]):
        shot = _screenshot(SHOT_DIR / f"kalodata_apply_{preset}_{i}.png")
        if use_vision and settings.has_gemini:
            coords = _gemini_click_hint(shot, step)
            if coords:
                client.click(*coords)
                time.sleep(1.5)
                continue
        print(f"[step {i+1}] {step} — manual/vision skip", file=sys.stderr)

    time.sleep(3)
    url = _capture_url_via_bar(client)
    if not url:
        shot = _screenshot(SHOT_DIR / f"kalodata_apply_{preset}_final.png")
        print(f"Could not read URL from clipboard. Screenshot: {shot}", file=sys.stderr)
        return ""

    block = kalodata_filters.preset_block(preset)
    data = kalodata_filters.load_config()
    data.setdefault("presets", {})[preset] = {**block, "filter_url": url}
    kalodata_filters.filters_path().write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return url


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply Kalodata filters on hub via desktop helper")
    parser.add_argument("preset", choices=sorted(PRESET_STEPS))
    parser.add_argument("--no-vision", action="store_true")
    parser.add_argument("--open-only", action="store_true")
    args = parser.parse_args()

    if args.open_only:
        _open_kalodata()
        print("Opened Kalodata in Edge")
        return 0

    try:
        url = apply_preset(args.preset, use_vision=not args.no_vision)
    except DesktopHubError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if url:
        print(f"OK saved {args.preset} filter_url ({len(url)} chars)")
        print(url)
        return 0
    print("Partial run — check screenshots in data/desktop_hub/", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
