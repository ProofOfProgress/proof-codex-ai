"""Scrape Discord from owner Edge session via desktop helper + Gemini (read-only)."""

from __future__ import annotations

import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.desktop_hub.client import DesktopHubClient, DesktopHubError

ROOT = Path(__file__).resolve().parents[2]
SHOT_DIR = settings.data_dir / "desktop_hub"
INBOX = settings.data_dir / "research" / "course" / "inbox"


def _gemini_extract_messages(image_path: Path) -> str:
    key = (settings.gemini_api_key or "").strip()
    if not key:
        return "(Gemini not configured — screenshot only)"
    try:
        from google import genai
    except ImportError:
        return "(google-genai not installed)"

    client = genai.Client(api_key=key)
    model = (settings.gemini_vision_model or settings.gemini_model or "gemini-2.5-flash-lite").strip()
    raw = image_path.read_bytes()
    prompt = (
        "This is a Discord channel screenshot in a web browser. "
        "Extract ALL visible chat messages as plain text. "
        "Format each line as: [author] message text. "
        "Include channel name if visible at top. "
        "Skip UI chrome, emoji reactions counts only if no message. "
        "If login page or not Discord, say NOT_DISCORD. "
        "Never invent messages."
    )
    try:
        resp = client.models.generate_content(
            model=model,
            contents=[prompt, genai.types.Part.from_bytes(data=raw, mime_type="image/png")],
        )
        return (resp.text or "").strip()
    except Exception as exc:
        return f"(Gemini error: {exc})"


def _desktop_cli(*args: str) -> None:
    subprocess.run(
        [sys.executable, "-m", "shorts_bot.desktop_hub.cli", *args],
        cwd=ROOT,
        check=True,
    )


def scrape_discord_desktop(
    *,
    scroll_passes: int = 40,
    screenshot_every: int = 2,
    pause_sec: float = 0.45,
) -> Path:
    """
    Read-only Discord scrape using logged-in Edge on Windows.
    Requires desktop helper running + owner logged into discord.com in browser.
    """
    client = DesktopHubClient()
    client.ping()

    INBOX.mkdir(parents=True, exist_ok=True)
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_path = INBOX / f"discord-desktop-crawl-{stamp}.md"

    lines = [
        f"# Discord desktop crawl — {stamp}",
        "",
        "**Read-only.** Edge session via desktop helper scroll + Gemini OCR.",
        "**Never sent messages.**",
        "",
    ]

    # Focus Edge: Win+1 often first taskbar app; then click center of screen
    try:
        _desktop_cli("hotkey", "win", "1")
        time.sleep(1.2)
        client.click(960, 540)
        time.sleep(0.5)
    except DesktopHubError:
        try:
            _desktop_cli("hotkey", "alt", "tab")
            time.sleep(0.8)
        except DesktopHubError:
            pass

    chunks: list[str] = []
    seen_hashes: set[str] = set()

    for i in range(scroll_passes):
        if i % screenshot_every == 0:
            shot = SHOT_DIR / f"discord_scroll_{i:03d}.png"
            result = client.screenshot()
            shot.write_bytes(result.png_bytes)
            text = _gemini_extract_messages(shot)
            if text and "NOT_DISCORD" not in text:
                digest = text[:200]
                if digest not in seen_hashes:
                    seen_hashes.add(digest)
                    chunks.append(f"## Scroll pass {i}\n\n{text}\n")
        try:
            client.press("pageup")
        except DesktopHubError:
            _desktop_cli("press", "pageup")
        time.sleep(pause_sec)

    # Final screenshot at top
    shot = SHOT_DIR / "discord_scroll_final.png"
    result = client.screenshot()
    shot.write_bytes(result.png_bytes)
    text = _gemini_extract_messages(shot)
    if text and "NOT_DISCORD" not in text:
        chunks.append(f"## Final (top)\n\n{text}\n")

    lines.extend(chunks or ["(No messages extracted — confirm Discord channel is visible in Edge)"])
    lines.append(f"\n---\n**Scroll passes:** {scroll_passes} · **Chunks:** {len(chunks)}\n")
    out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return out_path


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Discord desktop scrape (Edge + helper)")
    p.add_argument("--scroll", type=int, default=40)
    p.add_argument("--every", type=int, default=2)
    args = p.parse_args()
    path = scrape_discord_desktop(scroll_passes=args.scroll, screenshot_every=args.every)
    print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
