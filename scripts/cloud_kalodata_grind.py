#!/usr/bin/env python3
"""Cloud CEO drives Kalodata on hub: screenshot via SSH → Gemini on cloud → click via SSH."""

from __future__ import annotations

import argparse
import base64
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shorts_bot.config import settings
from shorts_bot.tiktok_shop import kalodata_filters
from shorts_bot.tiktok_shop.kalodata_preset_specs import launch_preset_keys, preset_by_key

HUB_SHOT = "data/desktop_hub/kalodata_live.png"
KALODATA_URL = "https://www.kalodata.com/product"


def _hub(*parts: str) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, "-m", "shorts_bot.hub_remote", "run", "--", *parts]
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)


def _open_kalodata() -> None:
    _hub("cmd.exe", "/c", f"start msedge {KALODATA_URL}")
    time.sleep(10)
    _hub(
        "cd",
        "~/proof-codex-ai",
        "&&",
        "python3",
        "-m",
        "shorts_bot.desktop_hub.cli",
        "hotkey",
        "alt",
        "tab",
    )


def _screenshot(local_path: Path) -> None:
    _hub(
        "cd",
        "~/proof-codex-ai",
        "&&",
        "python3",
        "-m",
        "shorts_bot.desktop_hub.cli",
        "screenshot",
        "--out",
        HUB_SHOT,
    )
    proc = _hub("cd", "~/proof-codex-ai", "&&", "base64", "-w0", HUB_SHOT)
    if proc.returncode != 0 or not proc.stdout.strip():
        raise RuntimeError(f"hub screenshot failed: {proc.stderr[:300]}")
    local_path.parent.mkdir(parents=True, exist_ok=True)
    local_path.write_bytes(base64.b64decode(proc.stdout.strip()))


def _gemini(step: str, image_path: Path) -> str:
    key = (settings.gemini_api_key or "").strip()
    if not key:
        return "SKIP"
    from google import genai

    client = genai.Client(api_key=key)
    model = (settings.gemini_model or "gemini-2.5-flash-lite").strip()
    prompt = (
        f"Kalodata product filter UI on Windows. Step: {step}\n"
        "Return ONE line: CLICK x y | TYPE text | PRESS keyname | DONE | SKIP"
    )
    resp = client.models.generate_content(
        model=model,
        contents=[prompt, genai.types.Part.from_bytes(data=image_path.read_bytes(), mime_type="image/png")],
    )
    return (resp.text or "").strip().splitlines()[0].strip()


def _act(line: str) -> None:
    if line.upper().startswith("CLICK"):
        m = re.search(r"CLICK\s+(\d+)\s+(\d+)", line, re.I)
        if m:
            _hub(
                "cd",
                "~/proof-codex-ai",
                "&&",
                "python3",
                "-m",
                "shorts_bot.desktop_hub.cli",
                "click",
                m.group(1),
                m.group(2),
            )
    elif line.upper().startswith("TYPE"):
        text = re.sub(r"^TYPE\s+", "", line, flags=re.I)
        _hub(
            "cd",
            "~/proof-codex-ai",
            "&&",
            "python3",
            "-m",
            "shorts_bot.desktop_hub.cli",
            "type",
            text,
        )
    elif line.upper().startswith("PRESS"):
        key = re.sub(r"^PRESS\s+", "", line, flags=re.I).strip().lower()
        _hub(
            "cd",
            "~/proof-codex-ai",
            "&&",
            "python3",
            "-m",
            "shorts_bot.desktop_hub.cli",
            "press",
            key,
        )


def _capture_url() -> str:
    _hub(
        "cd",
        "~/proof-codex-ai",
        "&&",
        "python3",
        "-m",
        "shorts_bot.desktop_hub.cli",
        "click",
        "640",
        "52",
        "--clicks",
        "3",
    )
    time.sleep(0.3)
    _hub(
        "cd",
        "~/proof-codex-ai",
        "&&",
        "python3",
        "-m",
        "shorts_bot.desktop_hub.cli",
        "hotkey",
        "ctrl",
        "c",
    )
    time.sleep(0.5)
    proc = _hub("powershell.exe", "-NoProfile", "-Command", "Get-Clipboard")
    lines = [ln.strip() for ln in (proc.stdout or "").splitlines() if ln.strip()]
    for ln in reversed(lines):
        if ln.startswith("http") and "kalodata" in ln.lower():
            return ln
    return ""


def _save_url(key: str, url: str) -> None:
    data = kalodata_filters.load_config()
    presets = data.setdefault("presets", {})
    block = presets.get(key) if isinstance(presets.get(key), dict) else {}
    presets[key] = {**block, "filter_url": url}
    kalodata_filters.filters_path().write_text(
        __import__("json").dumps(data, indent=2) + "\n",
        encoding="utf-8",
    )
    # push to hub
    subprocess.run(
        [
            sys.executable,
            "-m",
            "shorts_bot.hub_remote",
            "run",
            "--",
            f"cd ~/proof-codex-ai && git pull --ff-only origin cursor/scout-research-backends-ba97",
        ],
        cwd=ROOT,
        check=False,
    )


def grind_preset(key: str, *, steps: int = 12) -> str:
    spec = preset_by_key(key)
    if not spec:
        raise SystemExit(f"unknown preset {key}")
    _open_kalodata()
    local = settings.data_dir / "desktop_hub" / f"grind_{key}.png"
    for i, step in enumerate(spec.steps[:steps]):
        _screenshot(local)
        action = _gemini(step, local)
        print(f"[{key}] {i+1}: {action}", flush=True)
        if action.upper() == "DONE":
            break
        _act(action)
        time.sleep(1.0)
    time.sleep(2)
    url = _capture_url()
    if url:
        _save_url(key, url)
    return url


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preset", default="")
    parser.add_argument("--launch", action="store_true")
    args = parser.parse_args()
    keys = launch_preset_keys() if args.launch else [args.preset]
    if not keys[0]:
        parser.error("--preset or --launch required")
    ok = 0
    for key in keys:
        try:
            url = grind_preset(key)
            print(f"{'OK' if url else 'WARN'} {key} {url[:80] if url else ''}")
            if url:
                ok += 1
        except Exception as exc:
            print(f"ERROR {key}: {exc}", file=sys.stderr)
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
