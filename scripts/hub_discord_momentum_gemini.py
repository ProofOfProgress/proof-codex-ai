#!/usr/bin/env python3
"""Gemini OCR summarize Discord Momentum screenshots → inbox markdown."""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shorts_bot.agent_credentials import load_agent_credentials
from shorts_bot.config import settings


def main() -> int:
    load_agent_credentials()
    key = (os.environ.get("GEMINI_API_KEY") or settings.gemini_api_key or "").strip()
    if not key:
        print("No GEMINI_API_KEY", file=sys.stderr)
        return 1

    from google import genai

    shot_dir = settings.data_dir / "desktop_hub" / "discord_momentum"
    shots = sorted(shot_dir.glob("*.png"))
    if not shots:
        print("No screenshots — run hub_discord_momentum_scrape.py first", file=sys.stderr)
        return 2

    client = genai.Client(api_key=key)
    model = (os.environ.get("GEMINI_MODEL") or settings.gemini_model or "gemini-2.5-flash-lite").strip()
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out = settings.data_dir / "research" / "course" / "inbox" / f"discord-momentum-scrape-{stamp}.md"
    out.parent.mkdir(parents=True, exist_ok=True)

    lines = [f"# Discord Momentum scrape — {stamp}", "", f"Source: {len(shots)} screenshots", ""]
    # Sample every N to limit API (coach intel, not exhaustive OCR).
    step = max(1, len(shots) // 25)
    sample = shots[::step][:25]

    for path in sample:
        try:
            resp = client.models.generate_content(
                model=model,
                contents=[
                    "Extract coach/product-research relevant messages from this Discord screenshot. "
                    "Bullet points only. Skip UI chrome. Note any product names, filters, GMV, commission tips.",
                    genai.types.Part.from_bytes(data=path.read_bytes(), mime_type="image/png"),
                ],
            )
            text = (resp.text or "").strip()
            if text:
                lines.extend([f"## {path.name}", "", text, ""])
        except Exception as exc:
            lines.extend([f"## {path.name}", "", f"(ocr skip: {exc})", ""])

    out.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"OK {out} ({len(sample)} samples)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
