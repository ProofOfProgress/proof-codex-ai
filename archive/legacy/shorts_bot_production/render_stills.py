from __future__ import annotations

import math
import random
from pathlib import Path

from shorts_bot.production.image_prompts import ImageBrief


def _try_pillow():
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return None, None
    return Image, ImageDraw


def render_still(brief: ImageBrief, out_path: Path, *, seed: int | None = None) -> bool:
    """Render 9:16 calm still frame (no login, no external API)."""
    Image, ImageDraw = _try_pillow()
    if Image is None:
        return False

    rng = random.Random(seed if seed is not None else int(brief.start_seconds * 1000))
    w, h = 1080, 1920
    img = Image.new("RGB", (w, h), "#0B1020")
    draw = ImageDraw.Draw(img)

    # Soft gradient bands
    for i in range(h):
        t = i / h
        r = int(11 + 20 * t)
        g = int(16 + 35 * t)
        b = int(32 + 60 * t)
        draw.line([(0, i), (w, i)], fill=(r, g, b))

    cx, cy = w // 2, int(h * 0.42)
    pulse = 0.85 + 0.15 * math.sin(brief.start_seconds * 0.7)
    radius = int(120 * pulse)
    ring = "#8EB8FF"
    draw.ellipse(
        [cx - radius, cy - radius, cx + radius, cy + radius],
        outline=ring,
        width=4,
    )
    inner = radius // 2
    draw.ellipse(
        [cx - inner, cy - inner, cx + inner, cy + inner],
        fill="#1a2d4a",
        outline="#F2F5FA",
        width=2,
    )

    # Subtle floor line — grounding
    y_floor = int(h * 0.72)
    draw.line([(w * 0.2, y_floor), (w * 0.8, y_floor)], fill="#1a2744", width=3)

    # Soft mist dots
    for _ in range(24):
        x = rng.randint(80, w - 80)
        y = rng.randint(int(h * 0.15), int(h * 0.85))
        sz = rng.randint(2, 6)
        draw.ellipse([x, y, x + sz, y + sz], fill="#8EB8FF")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG")
    return True


def render_all_stills(briefs: list[ImageBrief], images_dir: Path) -> int:
    count = 0
    for b in briefs:
        path = images_dir / f"{b.filename_stem}.png"
        if render_still(b, path):
            count += 1
    return count
