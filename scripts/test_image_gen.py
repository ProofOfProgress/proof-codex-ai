#!/usr/bin/env python3
"""One-image smoke test for pay-as-you-go image API (Fal or Replicate)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shorts_bot.config import settings
from shorts_bot.production.images.router import generate_image


def main() -> None:
    out = settings.data_dir / "tiktok_shop" / "bubble_wrap" / "_test" / "api_smoke.png"
    prompt = (
        "Vertical 9:16 photorealistic photo of a whole orange wrapped in one layer of "
        "clear bubble wrap, neutral gray background, no text, no watermark."
    )
    provider = (settings.image_provider or "replicate").strip().lower()
    print(f"Provider: {provider}")
    if provider == "fal" and not settings.has_fal_images:
        raise SystemExit("FAL_API_KEY missing — see docs/FOR_OWNER_IMAGE_GEN.md")
    if provider == "replicate" and not settings.has_replicate_images:
        raise SystemExit("REPLICATE_API_TOKEN missing — see docs/FOR_OWNER_IMAGE_GEN.md")

    label = generate_image(prompt, out)
    print(f"OK → {out} ({label})")


if __name__ == "__main__":
    main()
