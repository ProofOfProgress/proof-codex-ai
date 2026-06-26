# Tests — Gemini Module 4 image generation

from pathlib import Path
from unittest.mock import MagicMock, patch

from shorts_bot.tiktok_shop.image_gen import enrich_prompt, generate_product_image


def test_enrich_prompt_adds_course_rules():
    out = enrich_prompt("Luxury serum on marble vanity")
    assert "Module 4" in out
    assert "Luxury serum on marble vanity" in out


def test_generate_product_image_calls_gemini(tmp_path, monkeypatch):
    fake_settings = type(
        "S",
        (),
        {
            "data_dir": tmp_path,
            "image_provider": "gemini",
            "has_gemini": True,
            "gemini_api_key": "test-key",
            "gemini_image_model": "gemini-3-pro-image-preview",
            "gemini_image_fast_model": "gemini-3.1-flash-image-preview",
            "gemini_image_size": "2K",
            "image_aspect_ratio": "9:16",
        },
    )()

    monkeypatch.setattr("shorts_bot.tiktok_shop.image_gen.settings", fake_settings)

    captured: dict = {}

    def fake_gen(prompt, out_path, **kwargs):
        captured["prompt"] = prompt
        captured["out"] = out_path
        captured["kwargs"] = kwargs
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(b"png")
        return "gemini/test"

    monkeypatch.setattr("shorts_bot.tiktok_shop.image_gen.generate_gemini_image", fake_gen)

    dest = generate_product_image("Vitamin C bottle on shelf", slug="vitamin")
    assert dest.is_file()
    assert "Module 4" in captured["prompt"]
    assert captured["kwargs"]["model"] == "gemini-3-pro-image-preview"


def test_router_gemini_provider(tmp_path, monkeypatch):
    from shorts_bot.production.images.router import generate_image

    fake_settings = type(
        "S",
        (),
        {
            "image_provider": "gemini",
            "has_gemini_images": True,
            "gemini_api_key": "k",
            "gemini_image_model": "gemini-3-pro-image-preview",
            "gemini_image_size": "2K",
            "image_aspect_ratio": "9:16",
            "has_fal_images": False,
            "has_replicate_images": False,
        },
    )()
    monkeypatch.setattr("shorts_bot.production.images.router.settings", fake_settings)

    with patch("shorts_bot.production.images.router.generate_gemini_image") as mock_gen:
        mock_gen.return_value = "gemini/x"
        out = tmp_path / "out.png"
        label = generate_image("hello", out)
        assert label == "gemini/x"
        mock_gen.assert_called_once()
