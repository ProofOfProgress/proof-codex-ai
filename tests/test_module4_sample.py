"""Module 4 Gemini sample image generation."""

from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from shorts_bot.tiktok_shop.module4_sample import (
    build_sample_prompt,
    generate_module4_sample,
    sample_image_path,
)


def test_build_sample_prompt_mentions_916():
    text = build_sample_prompt(product_name="Insulated Tumbler", style="kitchen")
    assert "9:16" in text
    assert "NO letterbox" in text
    assert "Insulated Tumbler" in text


def test_sample_image_path_slug():
    p = sample_image_path("Car Phone Mount")
    assert p.name == "car_phone_mount_916.jpg"


def test_generate_module4_sample_cached(tmp_path, monkeypatch):
    class FakeSettings:
        data_dir = tmp_path
        gemini_api_key = "x"
        gemini_image_model = "gemini-2.5-flash-image"

        @property
        def has_gemini(self):
            return True

    monkeypatch.setattr("shorts_bot.tiktok_shop.module4_sample.settings", FakeSettings())

    src = tmp_path / "listing.jpg"
    Image.new("RGB", (800, 800), (200, 100, 50)).save(src)
    dest = sample_image_path("Test Product")
    dest.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (1080, 1920), (10, 20, 30)).save(dest)

    result = generate_module4_sample(product_name="Test Product", source_image=src)
    assert result.model == "cached"
    assert result.width == 1080


def test_generate_module4_sample_calls_gemini(tmp_path, monkeypatch):
    class FakeSettings:
        data_dir = tmp_path
        gemini_api_key = "test-key"
        gemini_image_model = "gemini-2.5-flash-image"

        @property
        def has_gemini(self):
            return True

    monkeypatch.setattr("shorts_bot.tiktok_shop.module4_sample.settings", FakeSettings())

    src = tmp_path / "listing.jpg"
    Image.new("RGB", (512, 512), (255, 0, 0)).save(src)

    fake_img = Image.new("RGB", (768, 1344), (100, 150, 200))
    buf = BytesIO()
    fake_img.save(buf, format="JPEG")
    jpeg_bytes = buf.getvalue()

    inline = MagicMock()
    inline.inline_data = MagicMock()
    inline.inline_data.data = jpeg_bytes

    fake_resp = MagicMock()
    fake_resp.parts = [inline]

    fake_client = MagicMock()
    fake_client.models.generate_content.return_value = fake_resp

    with patch("shorts_bot.tiktok_shop.module4_sample._require_gemini_client", return_value=fake_client):
        result = generate_module4_sample(product_name="Gadget", source_image=src, force=True)

    assert result.sample_path.is_file()
    assert result.width == 1080
    assert result.height == 1920
    out = Image.open(result.sample_path)
    assert out.getpixel((0, 0)) != (42, 42, 44)


def test_generate_requires_gemini_key(tmp_path, monkeypatch):
    class FakeSettings:
        data_dir = tmp_path
        gemini_api_key = None

        @property
        def has_gemini(self):
            return False

    monkeypatch.setattr("shorts_bot.tiktok_shop.module4_sample.settings", FakeSettings())
    src = tmp_path / "x.jpg"
    src.write_bytes(b"x")
    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        generate_module4_sample(product_name="X", source_image=src, force=True)
