#!/usr/bin/env python3
"""Pull Discord scroll screenshots from hub and extract text with Gemini (cloud VM)."""

from __future__ import annotations

import re
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from shorts_bot.config import settings
from shorts_bot.integrations.discord_desktop_scrape import _gemini_extract_messages

INBOX = ROOT / "data" / "research" / "course" / "inbox"
SHOT_DIR = ROOT / "data" / "desktop_hub"


def _pull_shots() -> list[Path]:
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    b64_path = "/tmp/discord_shots.b64"
    pack = (
        "cd ~/proof-codex-ai && "
        "tar czf - data/desktop_hub/discord_scroll_*.png 2>/dev/null | base64 -w0 > " + b64_path
    )
    subprocess.run(
        [sys.executable, "-m", "shorts_bot.hub_remote", "run", pack],
        cwd=ROOT,
        check=True,
    )
    proc = subprocess.run(
        [sys.executable, "-m", "shorts_bot.hub_remote", "run", f"cat {b64_path}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    lines = [ln for ln in proc.stdout.splitlines() if ln and not ln.startswith("Tailscale")]
    if not lines:
        return sorted(SHOT_DIR.glob("discord_scroll_*.png"))
    import base64

    raw = base64.b64decode("".join(lines))
    with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp:
        tmp.write(raw)
        tar_path = Path(tmp.name)
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(ROOT)
    tar_path.unlink(missing_ok=True)
    return sorted(SHOT_DIR.glob("discord_scroll_*.png"))


def main() -> int:
    if not settings.has_gemini:
        print("GEMINI_API_KEY required on cloud VM", file=sys.stderr)
        return 1

    shots = _pull_shots()
    if not shots:
        print("No discord_scroll_*.png on hub — run hub_discord_desktop_scrape.sh first", file=sys.stderr)
        return 1

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out = INBOX / f"discord-desktop-crawl-{stamp}.md"
    INBOX.mkdir(parents=True, exist_ok=True)

    lines = [
        f"# Discord desktop crawl — {stamp}",
        "",
        "**Read-only.** Edge + desktop helper screenshots, Gemini extract on cloud.",
        "",
    ]
    seen: set[str] = set()
    for shot in shots:
        text = _gemini_extract_messages(shot)
        if not text or "NOT_DISCORD" in text:
            continue
        key = re.sub(r"\s+", " ", text[:180])
        if key in seen:
            continue
        seen.add(key)
        lines.extend([f"## {shot.name}", "", text, ""])

    out.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"OK {len(seen)} chunks → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
