"""Paid AI still frames — Replicate/Fal + bottom captions."""

from __future__ import annotations

from pathlib import Path

from shorts_bot.production.caption_overlay import apply_bottom_caption
from shorts_bot.production.image_prompts import ImageBrief
from shorts_bot.production.images.router import generate_image


def render_ai_frame(brief: ImageBrief, out_path: Path) -> bool:
    try:
        provider = generate_image(brief.prompt, out_path)
        apply_bottom_caption(out_path, brief.spoken_text)
        return True
    except Exception as exc:
        # Leave a marker for debugging; caller may fall back
        err_path = out_path.with_suffix(".error.txt")
        err_path.write_text(str(exc), encoding="utf-8")
        return False


def render_all_ai_images(briefs: list[ImageBrief], images_dir: Path) -> int:
    count = 0
    for b in briefs:
        path = images_dir / f"{b.filename_stem}.png"
        if render_ai_frame(b, path):
            count += 1
    return count
