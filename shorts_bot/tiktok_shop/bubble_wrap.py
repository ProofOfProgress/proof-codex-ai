"""Bubble wrap growth posts — 2-slide TikTok photo carousels (Module 2).

NOT affiliate MP4s. TikTok format = 2 images + manual swipe + Mackenzie sound.
Optional preview MP4 is for owner review only — do not post as video.
"""

from __future__ import annotations

import re
import subprocess
import unicodedata
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from shorts_bot.config import settings
from shorts_bot.tiktok_shop.captions import validate_hook_lines, wrap_hook_lines
from shorts_bot.tiktok_shop.product_images import prepare_vertical_9x16, strip_letterbox_bars
from shorts_bot.tiktok_shop.video_editor import DEFAULT_FONT

TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920
SLIDE1_MAX_CHARS = 18  # hook slide — wider lines clip on TikTok
SLIDE2_MAX_CHARS = 20  # CTA slide
SAFE_TEXT_WIDTH = 920  # px margin inside 1080 canvas

SLIDE2_CTA_LINES = (
    "Pause = Pop 💥",
    "Follow = Loud pop 🔊",
    "Share = Giant pop 🦖",
    "Comment = Big pop 💥💥",
)

EMOJI_FONT = Path("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf")
EMOJI_FONT_SIZE = 109  # Noto Color Emoji native raster size
EMOJI_HEIGHT_RATIO = 0.9  # display height vs caption font — inline with text, not oversized


def wrap_bubble_lines(text: str, *, slide: int = 1) -> list[str]:
    """Wrap bubble captions — slide 1 max 18 chars/line, slide 2 max 20."""
    limit = SLIDE1_MAX_CHARS if slide == 1 else SLIDE2_MAX_CHARS
    lines = wrap_hook_lines(text, max_chars_per_line=limit)
    bad = validate_hook_lines(lines, max_chars=limit)
    if bad:
        raise ValueError(f"Bubble text exceeds {limit} chars/line: {bad!r}")
    return lines


def _caption_font_size() -> int:
    return int(getattr(settings, "tiktok_shop_caption_font_size", 48) or 48)


def _caption_stroke_width(font_size: int) -> int:
    return max(2, font_size // 8)

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


def _load_emoji_font() -> ImageFont.FreeTypeFont | None:
    if not EMOJI_FONT.is_file():
        return None
    try:
        return ImageFont.truetype(str(EMOJI_FONT), size=EMOJI_FONT_SIZE)
    except OSError:
        return None


def _is_emoji_char(ch: str) -> bool:
    if not ch or ch in {" ", "\t"}:
        return False
    if ord(ch) in {0xFE0F, 0x200D}:
        return True
    cat = unicodedata.category(ch)
    if cat in {"So", "Sk"}:
        return True
    code = ord(ch)
    return 0x1F300 <= code <= 0x1FAFF or 0x2600 <= code <= 0x27BF


def _split_runs(text: str) -> list[tuple[str, bool]]:
    runs: list[tuple[str, bool]] = []
    buf = ""
    emoji: bool | None = None
    for ch in text:
        is_em = _is_emoji_char(ch)
        if buf and is_em != emoji:
            runs.append((buf, bool(emoji)))
            buf = ""
        buf += ch
        emoji = is_em
    if buf:
        runs.append((buf, bool(emoji)))
    return runs


def _segment_size(text: str, font: ImageFont.FreeTypeFont | ImageFont.ImageFont) -> tuple[int, int, int, int]:
    bbox = font.getbbox(text)
    return bbox[2] - bbox[0], bbox[3] - bbox[1], bbox[0], bbox[1]


def _emoji_display_height(text_size: int) -> int:
    return max(28, int(text_size * EMOJI_HEIGHT_RATIO))


def _emoji_raster(
    run: str,
    emoji_font: ImageFont.FreeTypeFont,
    display_height: int,
) -> tuple[Image.Image, int, int]:
    """Render emoji at native size, scale down to sit inline with caption text."""
    canvas = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    ImageDraw.Draw(canvas).text((0, 0), run, font=emoji_font, embedded_color=True)
    bbox = canvas.getbbox()
    if not bbox:
        return canvas, 0, 0
    cropped = canvas.crop(bbox)
    scale = display_height / max(1, cropped.height)
    width = max(1, int(cropped.width * scale))
    resized = cropped.resize((width, display_height), Image.Resampling.LANCZOS)
    return resized, width, display_height


def _emoji_run_width(
    run: str,
    emoji_font: ImageFont.FreeTypeFont | None,
    display_height: int,
) -> int:
    if not emoji_font:
        return 0
    _, width, _ = _emoji_raster(run, emoji_font, display_height)
    return width


def _fit_font_size(lines: list[str], base_size: int) -> int:
    """Shrink text if any line would exceed the safe canvas width."""
    size = base_size
    while size >= 28:
        text_font = _load_font(size)
        emoji_font = _load_emoji_font()
        emoji_h = _emoji_display_height(size)
        too_wide = False
        for line in lines:
            width = 0
            for run, is_emoji in _split_runs(line):
                if is_emoji and emoji_font:
                    width += _emoji_run_width(run, emoji_font, emoji_h)
                else:
                    w, _, _, _ = _segment_size(run, text_font)
                    width += w
            if width > SAFE_TEXT_WIDTH:
                too_wide = True
                break
        if not too_wide:
            return size
        size -= 2
    return max(28, size)


def _draw_mixed_centered_line(
    img: Image.Image,
    draw: ImageDraw.ImageDraw,
    line: str,
    *,
    center_x: float,
    center_y: float,
    text_font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    emoji_font: ImageFont.FreeTypeFont | ImageFont.ImageFont | None,
    stroke_width: int,
) -> None:
    """Draw one centered line — DejaVu for text, scaled Noto Color Emoji inline."""
    emoji_h = _emoji_display_height(text_font.size if hasattr(text_font, "size") else _caption_font_size())
    segments: list[tuple[str, bool, int, int, int]] = []
    total_w = 0
    text_ascent, text_descent = text_font.getmetrics()
    max_ascent = text_ascent
    max_descent = text_descent
    for run, is_emoji in _split_runs(line):
        if is_emoji and emoji_font:
            width = _emoji_run_width(run, emoji_font, emoji_h)
            segments.append((run, True, width, emoji_h, 0))
            max_ascent = max(max_ascent, emoji_h // 2)
            max_descent = max(max_descent, emoji_h // 2)
        else:
            w, _h, left, _top = _segment_size(run, text_font)
            segments.append((run, False, w, text_ascent, left))
        total_w += segments[-1][2]

    x = center_x - total_w / 2
    baseline_y = center_y + (max_ascent - max_descent) / 2
    for run, is_emoji, width, metric, left in segments:
        if is_emoji and emoji_font:
            patch, _, patch_h = _emoji_raster(run, emoji_font, emoji_h)
            y = int(center_y - patch_h / 2)
            img.paste(patch, (int(x), y), patch)
        else:
            y = baseline_y - metric
            draw.text(
                (x - left, y),
                run,
                font=text_font,
                fill="white",
                stroke_width=stroke_width,
                stroke_fill="black",
            )
        x += width


def burn_centered_lines(
    img: Image.Image,
    lines: list[str],
    *,
    y_fraction: float = 0.11,
    font_size: int | None = None,
    max_chars: int = SLIDE2_MAX_CHARS,
) -> Image.Image:
    """White bold text, black outline, emoji support, each line truly centered."""
    if not lines:
        return img
    bad = validate_hook_lines(lines, max_chars=max_chars)
    if bad:
        raise ValueError(f"Line exceeds {max_chars} char cap: {bad!r}")

    out = img.copy().convert("RGBA")
    draw = ImageDraw.Draw(out)
    base = font_size if font_size is not None else _caption_font_size()
    size = _fit_font_size(lines, base)
    text_font = _load_font(size)
    emoji_font = _load_emoji_font()
    stroke = _caption_stroke_width(size)
    w, h = out.size
    step = max(1, int(size * 1.25))
    for i, line in enumerate(lines):
        y = int(h * y_fraction + i * step)
        _draw_mixed_centered_line(
            out,
            draw,
            line,
            center_x=w / 2,
            center_y=y,
            text_font=text_font,
            emoji_font=emoji_font,
            stroke_width=stroke,
        )
    return out.convert("RGB")


def burn_slide1_text(img: Image.Image, hook: str) -> Image.Image:
    lines = wrap_bubble_lines(hook.strip(), slide=1)
    return burn_centered_lines(img, lines, y_fraction=0.12, max_chars=SLIDE1_MAX_CHARS)


def burn_slide2_text(img: Image.Image, lines: tuple[str, ...] | None = None) -> Image.Image:
    rows: list[str] = []
    for line in lines or SLIDE2_CTA_LINES:
        rows.extend(wrap_bubble_lines(line.strip(), slide=2))
    return burn_centered_lines(img, rows, y_fraction=0.28, max_chars=SLIDE2_MAX_CHARS)


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
    slide1_raw_path = out_dir / "slide1_raw.jpg"
    slide2_raw_path = out_dir / "slide2_raw.jpg"
    preview_path = out_dir / "preview.mp4"

    model = (settings.gemini_image_model or "gemini-2.5-flash-image").strip()

    if not force and slide1_path.is_file() and slide2_path.is_file():
        prev = preview_path if preview and preview_path.is_file() else None
        return BubbleWrapResult(subj, hook_text, slide1_path, slide2_path, prev, "cached")

    raw1 = _gemini_image(build_slide1_prompt(subj))
    base1 = _finalize_image(raw1)
    base1.save(slide1_raw_path, format="JPEG", quality=92)
    img1 = burn_slide1_text(base1, hook_text)
    img1.save(slide1_path, format="JPEG", quality=92)
    hook_sidecar = out_dir / "slide1_hook.txt"
    hook_sidecar.write_text("\n".join(wrap_bubble_lines(hook_text, slide=1)) + "\n", encoding="utf-8")

    raw2 = _gemini_image(build_slide2_prompt(subj))
    base2 = _finalize_image(raw2)
    base2.save(slide2_raw_path, format="JPEG", quality=92)
    img2 = burn_slide2_text(base2)
    img2.save(slide2_path, format="JPEG", quality=92)
    out_dir.joinpath("slide2_cta.txt").write_text(
        "\n".join(
            ln
            for line in SLIDE2_CTA_LINES
            for ln in wrap_bubble_lines(line.strip(), slide=2)
        )
        + "\n",
        encoding="utf-8",
    )

    prev: Path | None = None
    if preview:
        prev = make_preview_mp4(slide1_path, slide2_path, preview_path)

    return BubbleWrapResult(subj, hook_text, slide1_path, slide2_path, prev, model)


def rebake_bubble_captions(
    *,
    account: str = "",
    subject: str = "frog",
    hook: str = "",
    preview: bool = True,
) -> BubbleWrapResult:
    """Re-burn captions on saved raw slides — no Gemini regen."""
    subj = (subject or "frog").strip()
    hook_text = (hook or default_hook(subj)).strip()
    slug = _slug(account or subj)
    out_dir = output_dir() / slug
    slide1_raw = out_dir / "slide1_raw.jpg"
    slide2_raw = out_dir / "slide2_raw.jpg"
    if not slide1_raw.is_file() or not slide2_raw.is_file():
        raise FileNotFoundError(f"Missing raw slides in {out_dir} — run bubble-slides --force first")

    slide1_path = out_dir / "slide1_hook.jpg"
    slide2_path = out_dir / "slide2_cta.jpg"
    preview_path = out_dir / "preview.mp4"

    img1 = burn_slide1_text(Image.open(slide1_raw).convert("RGB"), hook_text)
    img1.save(slide1_path, format="JPEG", quality=92)
    out_dir.joinpath("slide1_hook.txt").write_text(
        "\n".join(wrap_bubble_lines(hook_text, slide=1)) + "\n",
        encoding="utf-8",
    )

    img2 = burn_slide2_text(Image.open(slide2_raw).convert("RGB"))
    img2.save(slide2_path, format="JPEG", quality=92)
    out_dir.joinpath("slide2_cta.txt").write_text(
        "\n".join(
            ln
            for line in SLIDE2_CTA_LINES
            for ln in wrap_bubble_lines(line.strip(), slide=2)
        )
        + "\n",
        encoding="utf-8",
    )

    prev: Path | None = None
    if preview:
        prev = make_preview_mp4(slide1_path, slide2_path, preview_path)

    return BubbleWrapResult(subj, hook_text, slide1_path, slide2_path, prev, "rebaked")
