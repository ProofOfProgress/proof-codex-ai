#!/usr/bin/env python3
"""Capture Kalodata filter URLs on hub via desktop helper + Gemini vision (cloud-run)."""

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
from shorts_bot.tiktok_shop.kalodata_preset_specs import PRESETS, launch_preset_keys, preset_by_key

KALODATA_PRODUCT = "https://www.kalodata.com/product"
SHOT_DIR = settings.data_dir / "desktop_hub" / "kalodata_capture"


def _gemini_action(image_path: Path, goal: str) -> str:
    key = (settings.gemini_api_key or "").strip()
    if not key:
        return "SKIP"
    try:
        from google import genai
    except ImportError:
        return "SKIP"

    client = genai.Client(api_key=key)
    model = (settings.gemini_model or "gemini-2.5-flash-lite").strip()
    raw = image_path.read_bytes()
    prompt = (
        f"You are driving Kalodata product filters on a Windows desktop.\n"
        f"Goal: {goal}\n\n"
        "Return EXACTLY one line:\n"
        "- CLICK x y   (pixel coords on this screenshot)\n"
        "- TYPE text_here   (for typing into focused field)\n"
        "- SCROLL down   (if need to reach Submit)\n"
        "- DONE   (filters applied and results visible)\n"
        "- SKIP   (cannot see target)\n"
    )
    try:
        resp = client.models.generate_content(
            model=model,
            contents=[prompt, genai.types.Part.from_bytes(data=raw, mime_type="image/png")],
        )
        return (resp.text or "").strip().splitlines()[0].strip()
    except Exception:
        return "SKIP"


def _open_edge_kalodata() -> None:
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
    time.sleep(10)
    client = DesktopHubClient()
    client.hotkey("alt", "tab")
    time.sleep(1)


def _clipboard_url() -> str:
    proc = subprocess.run(
        [sys.executable, "-m", "shorts_bot.hub_remote", "run", "--", "powershell.exe -NoProfile -Command Get-Clipboard"],
        capture_output=True,
        text=True,
        check=False,
    )
    url = (proc.stdout or "").strip().splitlines()[-1] if proc.stdout else ""
    if url.startswith("http") and "kalodata" in url.lower():
        return url
    return ""


def _capture_url(client: DesktopHubClient) -> str:
    client.click(640, 52, clicks=3)
    time.sleep(0.2)
    client.hotkey("ctrl", "c")
    time.sleep(0.4)
    return _clipboard_url()


def _save_url(preset_key: str, url: str) -> None:
    if not url or "/product/detail" in url.lower():
        raise RuntimeError(f"Invalid list URL for {preset_key}: {url[:80]!r}")
    data = kalodata_filters.load_config()
    presets = data.setdefault("presets", {})
    block = presets.get(preset_key) if isinstance(presets.get(preset_key), dict) else {}
    presets[preset_key] = {**block, "filter_url": url}
    kalodata_filters.filters_path().write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def capture_one(preset_key: str, *, max_steps: int = 14) -> str:
    spec = preset_by_key(preset_key)
    if not spec:
        raise SystemExit(f"Unknown preset {preset_key!r}")

    client = DesktopHubClient()
    client.ping()
    _open_edge_kalodata()

    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    for i, step in enumerate(spec.steps[:max_steps]):
        shot_path = SHOT_DIR / f"{preset_key}_{i:02d}.png"
        result = client.screenshot()
        shot_path.write_bytes(result.png_bytes)
        action = _gemini_action(shot_path, step)
        print(f"[{preset_key} {i+1}/{len(spec.steps)}] {action}", flush=True)
        if action.upper().startswith("CLICK"):
            m = re.search(r"CLICK\s+(\d+)\s+(\d+)", action, re.I)
            if m:
                client.click(int(m.group(1)), int(m.group(2)))
                time.sleep(1.2)
        elif action.upper().startswith("TYPE"):
            text = re.sub(r"^TYPE\s+", "", action, flags=re.I).strip()
            if text:
                client.type_text(text)
                time.sleep(0.5)
        elif action.upper() == "SCROLL DOWN":
            client.press("pagedown")
            time.sleep(0.8)
        elif action.upper() == "DONE":
            break
        time.sleep(0.5)

    time.sleep(3)
    url = _capture_url(client)
    if url:
        _save_url(preset_key, url)
    return url


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture Kalodata filter URLs on hub")
    parser.add_argument("--preset", default="", help="Single preset key")
    parser.add_argument("--launch", action="store_true", help="All P0 presets")
    parser.add_argument("--open-only", action="store_true")
    args = parser.parse_args()

    if args.open_only:
        _open_edge_kalodata()
        print("Opened Kalodata in Edge on hub")
        return 0

    keys = launch_preset_keys() if args.launch else [args.preset]
    if not keys or not keys[0]:
        parser.error("Use --preset KEY or --launch")

    ok = 0
    for key in keys:
        try:
            url = capture_one(key)
            if url:
                print(f"OK {key} → {url[:100]}...")
                ok += 1
            else:
                print(f"WARN {key} — no URL captured; see {SHOT_DIR}", file=sys.stderr)
        except DesktopHubError as exc:
            print(f"ERROR {key}: {exc}", file=sys.stderr)

    print(f"Captured {ok}/{len(keys)} preset URLs")
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
