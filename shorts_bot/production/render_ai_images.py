"""Paid AI still frames — Replicate/Fal + bottom captions."""

from __future__ import annotations

import time
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.production.captions import burn_captions_on_frames
from shorts_bot.production.caption_overlay import apply_bottom_caption
from shorts_bot.production.image_prompts import ImageBrief
from shorts_bot.production.images.router import generate_image


def render_ai_frame(brief: ImageBrief, out_path: Path) -> bool:
    try:
        provider = generate_image(brief.prompt, out_path, style_id=brief.recraft_style_id)
        if burn_captions_on_frames():
            apply_bottom_caption(out_path, brief.spoken_text)
        return True
    except Exception as exc:
        # Leave a marker for debugging; caller may fall back
        err_path = out_path.with_suffix(".error.txt")
        err_path.write_text(str(exc), encoding="utf-8")
        return False


def render_all_ai_images(briefs: list[ImageBrief], images_dir: Path) -> int:
    """Generate one AI still per segment; pace Replicate when credit is low."""
    pace_sec = 11.0 if (settings.image_provider or "").strip().lower() == "replicate" else 0.0
    count = 0
    for i, b in enumerate(briefs):
        if pace_sec and i > 0:
            time.sleep(pace_sec)
        path = images_dir / f"{b.filename_stem}.png"
        if render_ai_frame(b, path):
            count += 1
    return count
