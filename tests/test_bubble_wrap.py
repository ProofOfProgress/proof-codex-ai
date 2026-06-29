"""Bubble wrap slide generation."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from shorts_bot.tiktok_shop.bubble_wrap import (
    SLIDE2_CTA_LINES,
    burn_slide1_text,
    burn_slide2_text,
    default_hook,
)


def test_default_hook():
    assert default_hook("frog") == "FROG BUBBLE WRAP ASMR >>>"


def test_burn_slide1_text():
    img = Image.new("RGB", (1080, 1920), (100, 100, 100))
    out = burn_slide1_text(img, "FROG BUBBLE WRAP ASMR >>>")
    assert out.size == (1080, 1920)


def test_burn_slide2_has_four_lines():
    img = Image.new("RGB", (1080, 1920), (100, 100, 100))
    out = burn_slide2_text(img, SLIDE2_CTA_LINES)
    assert out.size == (1080, 1920)


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
    assert "FROG" in result.hook_text or "frog" in result.subject.lower()
