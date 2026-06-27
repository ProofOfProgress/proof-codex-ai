#!/usr/bin/env python3
"""One-shot bubble wrap slideshow: base images + caption overlay from sample layout."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shorts_bot.config import settings
from shorts_bot.tiktok_shop.bubble_wrap_layout import compose_cta_slide, compose_hook_slide
from shorts_bot.tiktok_shop.bubble_wrap_prompts import ORANGE_SLIDESHOW


def _out_dir(subject: str) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    return settings.data_dir / "tiktok_shop" / "bubble_wrap" / f"{subject}_{stamp}"


def run_orange(*, slide1_base: Path | None = None, slide2_base: Path | None = None) -> dict:
    out = _out_dir("orange")
    out.mkdir(parents=True, exist_ok=True)

    prompts_path = out / "prompts.json"
    prompts_path.write_text(json.dumps(ORANGE_SLIDESHOW, indent=2) + "\n", encoding="utf-8")

    s1_base = out / "slide1_base.png"
    s2_base = out / "slide2_base.png"

    if slide1_base and slide1_base.is_file():
        shutil.copy2(slide1_base, s1_base)
    else:
        from shorts_bot.production.images.router import generate_image

        generate_image(ORANGE_SLIDESHOW["slide1_hook"]["prompt"], s1_base)

    if slide2_base and slide2_base.is_file():
        shutil.copy2(slide2_base, s2_base)
    else:
        from shorts_bot.production.images.router import generate_image

        generate_image(ORANGE_SLIDESHOW["slide2_cta"]["prompt"], s2_base)

    s1_final = out / "slide1_hook.png"
    s2_final = out / "slide2_cta.png"
    compose_hook_slide(s1_base, s1_final)
    compose_cta_slide(s2_base, s2_final)

    return {
        "output_dir": str(out),
        "slide1_hook": str(s1_final),
        "slide2_cta": str(s2_final),
        "prompts": str(prompts_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Make bubble wrap 2-slide PNG pair")
    parser.add_argument("--subject", default="orange")
    parser.add_argument("--slide1-base", type=Path, default=None, help="Skip gen — use existing base PNG")
    parser.add_argument("--slide2-base", type=Path, default=None)
    args = parser.parse_args()

    if args.subject != "orange":
        raise SystemExit("Only orange subject is catalogued in bubble_wrap_prompts.py for now")

    result = run_orange(slide1_base=args.slide1_base, slide2_base=args.slide2_base)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
