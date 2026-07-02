#!/usr/bin/env python3
"""Pull hub Discord full scrape folder and Gemini-extract on cloud (with retries)."""

from __future__ import annotations

import base64
import re
import subprocess
import sys
import tarfile
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from shorts_bot.config import settings
from shorts_bot.integrations.discord_desktop_scrape import _gemini_extract_messages

INBOX = ROOT / "data" / "research" / "course" / "inbox"
SHOT_DIR = ROOT / "data" / "desktop_hub" / "discord_full"

_REDACT = re.compile(r"D3vil_Wolv3s|password", re.I)


def _pull_folder() -> list[Path]:
    b64_path = "/tmp/discord_full.b64"
    pack = (
        "cd ~/proof-codex-ai && "
        "tar czf - data/desktop_hub/discord_full 2>/dev/null | base64 -w0 > " + b64_path
    )
    subprocess.run([sys.executable, "-m", "shorts_bot.hub_remote", "run", pack], cwd=ROOT, check=True)
    proc = subprocess.run(
        [sys.executable, "-m", "shorts_bot.hub_remote", "run", f"cat {b64_path}"],
        capture_output=True,
        text=True,
    )
    lines = [ln for ln in proc.stdout.splitlines() if ln and not ln.startswith("Tailscale")]
    raw = base64.b64decode("".join(lines))
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp:
        tmp.write(raw)
        tar_path = Path(tmp.name)
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(ROOT)
    tar_path.unlink(missing_ok=True)
    return sorted(SHOT_DIR.glob("*.png"))


def _extract(path: Path) -> str:
    for attempt in range(4):
        text = _gemini_extract_messages(path)
        if "503" not in text and "UNAVAILABLE" not in text:
            return _REDACT.sub("[redacted]", text)
        time.sleep(2 ** attempt)
    return ""


def main() -> int:
    if not settings.has_gemini:
        print("GEMINI_API_KEY required", file=sys.stderr)
        return 1
    shots = _pull_folder()
    if not shots:
        # fallback: discord_scroll_*.png
        shots = sorted((ROOT / "data/desktop_hub").glob("discord_scroll_*.png"))
    if not shots:
        print("No screenshots on hub", file=sys.stderr)
        return 1

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out = INBOX / f"discord-full-crawl-{stamp}.md"
    INBOX.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Discord full crawl — {stamp}",
        "",
        "**Read-only.** Desktop helper multi-channel scrape + cloud Gemini.",
        "",
    ]
    seen: set[str] = set()
    for shot in shots:
        text = _extract(shot)
        if not text or "NOT_DISCORD" in text:
            continue
        key = re.sub(r"\s+", " ", text[:160])
        if key in seen or len(key) < 20:
            continue
        seen.add(key)
        lines.extend([f"## {shot.name}", "", text, ""])

    out.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"OK {len(seen)} chunks from {len(shots)} shots → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
