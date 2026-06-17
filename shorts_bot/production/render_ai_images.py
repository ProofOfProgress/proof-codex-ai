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
        from shorts_bot.production.lost_boy_image_lab import generate_still_with_qc

        if "lost boy" in brief.prompt.lower():
            from shorts_bot.production.image_prompts import (
                classify_lost_boy_shot,
                lost_boy_pose_requirements,
            )

            shot = classify_lost_boy_shot(brief.spoken_text)
            requirements = lost_boy_pose_requirements(shot)
            if shot in (
                "boy_waving_group",
                "group_tension",
            ):
                requirements += " Group shots need 2+ visible adult hikers plus the boy."
            return generate_still_with_qc(
                brief.prompt,
                out_path,
                style_id=brief.recraft_style_id,
                spoken_line=brief.spoken_text,
                requirements=requirements,
                max_attempts=3,
            )

        generate_image(brief.prompt, out_path, style_id=brief.recraft_style_id)
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
            continue
        # Fail-soft: one simplified retry so pipeline doesn't die on one frame
        safe_prompt = (
            f"Hand-drawn cartoon forest illustration: {b.spoken_text}. "
            "9:16 vertical still, no text, family-safe spooky comedy."
        )
        try:
            generate_image(safe_prompt, path, style_id=b.recraft_style_id)
            if path.is_file() and path.stat().st_size > 1000:
                count += 1
        except Exception:
            pass
    return count
