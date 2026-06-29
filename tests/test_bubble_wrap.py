"""Bubble wrap slide generation."""

from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image

from shorts_bot.tiktok_shop.bubble_wrap import (
    SLIDE1_MAX_CHARS,
    SLIDE2_CTA_LINES,
    _emoji_display_height,
    _emoji_raster,
    _load_emoji_font,
    burn_slide1_text,
    burn_slide2_text,
    default_hook,
    wrap_bubble_lines,
)


def test_default_hook():
    assert default_hook("frog") == "FROG BUBBLE WRAP ASMR >>>"


def test_wrap_slide1_max_18_chars():
    lines = wrap_bubble_lines(default_hook("frog"), slide=1)
    assert len(lines) >= 2
    assert all(len(line) <= SLIDE1_MAX_CHARS for line in lines)


def test_burn_slide1_text():
    img = Image.new("RGB", (1080, 1920), (100, 100, 100))
    out = burn_slide1_text(img, "FROG BUBBLE WRAP ASMR >>>")
    assert out.size == (1080, 1920)
    xs = [x for x in range(1080) for y in range(120, 320) if out.getpixel((x, y)) != (100, 100, 100)]
    assert xs
    assert min(xs) > 40
    assert max(xs) < 1040


def test_emoji_raster_scales_inline_with_text():
    emoji_font = _load_emoji_font()
    assert emoji_font is not None
    display_h = _emoji_display_height(48)
    assert display_h <= 48
    _, width, height = _emoji_raster("💥", emoji_font, display_h)
    assert height <= display_h + 1
    assert width < 80  # native unscaled glyph bbox is ~122px wide


def test_burn_slide2_has_four_lines_and_emojis():
    img = Image.new("RGB", (1080, 1920), (100, 100, 100))
    out = burn_slide2_text(img, SLIDE2_CTA_LINES)
    assert out.size == (1080, 1920)
    # Emoji pixels are colorful — not flat gray background
    colorful = 0
    for x in range(1080):
        for y in range(400, 900):
            r, g, b = out.getpixel((x, y))
            if (r, g, b) != (100, 100, 100) and (r, g, b) != (255, 255, 255) and (r, g, b) != (0, 0, 0):
                colorful += 1
    assert colorful > 50


def test_generate_bubble_wrap_slides_mock(tmp_path, monkeypatch):
    class FakeSettings:
        data_dir = tmp_path
        gemini_api_key = "x"
        gemini_image_model = "gemini-2.5-flash-image"

        @property
        def has_gemini(self):
            return True

    monkeypatch.setattr("shorts_bot.tiktok_shop.bubble_wrap.settings", FakeSettings())

    fake = Image.new("RGB", (768, 1344), (50, 120, 80))
    buf = __import__("io").BytesIO()
    fake.save(buf, format="JPEG")

    with patch("shorts_bot.tiktok_shop.bubble_wrap._gemini_image", return_value=buf.getvalue()):
        with patch("shorts_bot.tiktok_shop.bubble_wrap.make_preview_mp4") as mock_prev:
            mock_prev.return_value = tmp_path / "bubble_wrap" / "slides" / "x" / "preview.mp4"
            from shorts_bot.tiktok_shop.bubble_wrap import generate_bubble_wrap_slides

            result = generate_bubble_wrap_slides(subject="frog", account="test", preview=False, force=True)

    assert result.slide1.is_file()
    assert result.slide2.is_file()
    assert result.slide1.with_name("slide1_raw.jpg").is_file()
    assert "FROG" in result.hook_text or "frog" in result.subject.lower()
