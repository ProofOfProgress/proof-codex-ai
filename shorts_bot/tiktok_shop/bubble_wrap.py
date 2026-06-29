"""Bubble wrap growth posts — 2-slide TikTok photo carousels (Module 2).

NOT affiliate MP4s. TikTok format = 2 images + manual swipe + Mackenzie sound.
Optional preview MP4 is for owner review only — do not post as video.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from shorts_bot.config import settings
from shorts_bot.tiktok_shop.product_images import prepare_vertical_9x16, strip_letterbox_bars
from shorts_bot.tiktok_shop.video_editor import DEFAULT_FONT

TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920

SLIDE2_CTA_LINES = (
    "Pause = Pop 💥",
    "Follow = Loud pop 🔊",
    "Share = Giant pop 🦖",
    "Comment = Big pop 💥💥",
)


@dataclass
class BubbleWrapResult:
    subject: str
    hook_text: str
    slide1: Path
    slide2: Path
    preview_mp4: Path | None
    model: str


def _slug(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", name.lower()).strip("_")
    return slug[:48] or "bubble"


def output_dir() -> Path:
    return settings.data_dir / "bubble_wrap" / "slides"


def _require_gemini_client():
    if not settings.has_gemini:
        raise RuntimeError("GEMINI_API_KEY required for bubble wrap slides")
    from google import genai

    return genai.Client(api_key=settings.gemini_api_key)


def default_hook(subject: str) -> str:
    key = subject.strip().upper()
    if "ASMR" in key or ">>>" in key:
        return key
    return f"{key} BUBBLE WRAP ASMR >>>"


def build_slide1_prompt(subject: str) -> str:
    subj = subject.strip() or "frog"
    return (
        f"Photorealistic vertical TikTok photo, 9:16 full-bleed edge-to-edge — NO letterbox bars, "
        f"NO gray borders, NO text, NO watermarks. Subject: {subj} completely covered in clear "
        "bubble wrap with visible air bubbles, satisfying ASMR aesthetic, crisp detail, soft "
        "natural lighting, simple uncluttered background, viral bubble-wrap TikTok growth post style."
    )


def build_slide2_prompt(subject: str) -> str:
    subj = subject.strip() or "frog"
    return (
        f"Photorealistic vertical TikTok photo, 9:16 full-bleed — same concept: {subj} wrapped in "
        "clear bubble wrap, slightly different angle than before, visible bubbles, satisfying ASMR "
        "look, soft lighting, simple background, NO text, NO watermarks, NO gray letterbox bars."
    )


def _gemini_image(prompt: str) -> bytes:
    from google.genai import types

    client = _require_gemini_client()
    model = (settings.gemini_image_model or "gemini-2.5-flash-image").strip()
    resp = client.models.generate_content(
        model=model,
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(aspect_ratio="9:16"),
        ),
    )
    for part in resp.parts:
        if part.inline_data is not None:
            data = part.inline_data.data
            return data if isinstance(data, bytes) else bytes(data)
    text = getattr(resp, "text", "") or ""
    raise RuntimeError(f"Gemini returned no bubble wrap image. {text[:300]}")


def _finalize_image(raw_bytes: bytes) -> Image.Image:
    img = Image.open(BytesIO(raw_bytes)).convert("RGB")
    img = strip_letterbox_bars(img)
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=95)
    out = prepare_vertical_9x16(buf.getvalue())
    return Image.open(BytesIO(out)).convert("RGB")


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if DEFAULT_FONT.is_file():
        return ImageFont.truetype(str(DEFAULT_FONT), size=size)
    return ImageFont.load_default()


def _draw_outlined_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    text: str,
    *,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    fill: str = "white",
    stroke: str = "black",
    stroke_width: int = 6,
    anchor: str = "mm",
) -> None:
    draw.text(xy, text, font=font, fill=fill, anchor=anchor, stroke_width=stroke_width, stroke_fill=stroke)


def burn_slide1_text(img: Image.Image, hook: str) -> Image.Image:
    out = img.copy()
    draw = ImageDraw.Draw(out)
    font = _load_font(72)
    w, h = out.size
    _draw_outlined_text(draw, (w / 2, h * 0.18), hook.strip(), font=font, stroke_width=8)
    return out


def burn_slide2_text(img: Image.Image, lines: tuple[str, ...] | None = None) -> Image.Image:
    out = img.copy()
    draw = ImageDraw.Draw(out)
    font = _load_font(58)
    w, h = out.size
    rows = list(lines or SLIDE2_CTA_LINES)
    start_y = h * 0.28
    step = int(h * 0.11)
    for i, line in enumerate(rows):
        _draw_outlined_text(draw, (w / 2, start_y + i * step), line, font=font, stroke_width=7)
    return out


def make_preview_mp4(slide1: Path, slide2: Path, dest: Path, *, seconds_each: float = 3.0) -> Path:
    """Owner preview only — TikTok posts must use 2-photo carousel, not this MP4."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    dur = max(1.0, seconds_each)
    vf = (
        f"scale={TARGET_WIDTH}:{TARGET_HEIGHT}:force_original_aspect_ratio=decrease,"
        f"pad={TARGET_WIDTH}:{TARGET_HEIGHT}:(ow-iw)/2:(oh-ih)/2,"
        f"fps=30,format=yuv420p"
    )
    cmd = [
        "ffmpeg",
        "-y",
        "-loop",
        "1",
        "-t",
        str(dur),
        "-i",
        str(slide1),
        "-loop",
        "1",
        "-t",
        str(dur),
        "-i",
        str(slide2),
        "-filter_complex",
        f"[0:v]{vf}[v0];[1:v]{vf}[v1];[v0][v1]concat=n=2:v=1:a=0[outv]",
        "-map",
        "[outv]",
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "20",
        "-pix_fmt",
        "yuv420p",
        str(dest),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "")[-800:]
        raise RuntimeError(f"ffmpeg bubble preview failed: {tail}")
    return dest


def generate_bubble_wrap_slides(
    *,
    subject: str = "frog",
    hook: str = "",
    account: str = "",
    preview: bool = True,
    force: bool = False,
) -> BubbleWrapResult:
    subj = (subject or "frog").strip()
    hook_text = (hook or default_hook(subj)).strip()
    slug = _slug(account or subj)
    out_dir = output_dir() / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    slide1_path = out_dir / "slide1_hook.jpg"
    slide2_path = out_dir / "slide2_cta.jpg"
    preview_path = out_dir / "preview.mp4"

    model = (settings.gemini_image_model or "gemini-2.5-flash-image").strip()

    if not force and slide1_path.is_file() and slide2_path.is_file():
        prev = preview_path if preview and preview_path.is_file() else None
        return BubbleWrapResult(subj, hook_text, slide1_path, slide2_path, prev, "cached")

    raw1 = _gemini_image(build_slide1_prompt(subj))
    img1 = burn_slide1_text(_finalize_image(raw1), hook_text)
    img1.save(slide1_path, format="JPEG", quality=92)

    raw2 = _gemini_image(build_slide2_prompt(subj))
    img2 = burn_slide2_text(_finalize_image(raw2))
    img2.save(slide2_path, format="JPEG", quality=92)

    prev: Path | None = None
    if preview:
        prev = make_preview_mp4(slide1_path, slide2_path, preview_path)

    return BubbleWrapResult(subj, hook_text, slide1_path, slide2_path, prev, model)
