from pathlib import Path
from unittest.mock import patch

import pytest


def test_recraft_generate_posts_style_id(tmp_path: Path):
    from shorts_bot.production.images.recraft import generate_recraft_image

    out = tmp_path / "frame.png"
    captured: dict = {}

    def fake_request(method, path, *, api_key, payload=None, timeout=180):
        captured["method"] = method
        captured["path"] = path
        captured["payload"] = payload
        return {"data": [{"url": "https://example.com/img.png"}]}

    with patch("shorts_bot.production.images.recraft._request", side_effect=fake_request):
        with patch("shorts_bot.production.images.recraft._download_url") as dl:
            tag = generate_recraft_image(
                "crayon horror apartment",
                out,
                api_key="test-key-123456789012",
                model="recraftv3",
                style_id="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
                size="1024x1820",
            )

    assert captured["path"] == "/images/generations"
    assert captured["payload"]["model"] == "recraftv3"
    assert captured["payload"]["style_id"] == "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    assert captured["payload"]["size"] == "1024x1820"
    assert tag.startswith("recraft/recraftv3")
    dl.assert_called_once()


def test_probe_recraft_zero_balance():
    from shorts_bot.production.images.recraft import probe_recraft

    with patch(
        "shorts_bot.production.images.recraft._request",
        return_value={"credits": 0, "email": "owner@example.com"},
    ):
        ok, msg = probe_recraft("test-key-123456789012345")
    assert ok is False
    assert "0 API units" in msg


def test_router_recraft_provider(tmp_path: Path):
    from shorts_bot.config import Settings
    from shorts_bot.production.images.router import generate_image

    fake = Settings(
        image_provider="recraft",
        recraft_api_key="test-key-123456789012345",
        recraft_style_id="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
    )
    out = tmp_path / "out.png"

    with patch("shorts_bot.production.images.router.settings", fake):
        with patch(
            "shorts_bot.production.images.router.generate_recraft_image",
            return_value="recraft/recraftv3",
        ) as gen:
            assert generate_image("prompt", out) == "recraft/recraftv3"
            gen.assert_called_once()

    missing = Settings(image_provider="recraft", recraft_api_key=None)
    with patch("shorts_bot.production.images.router.settings", missing):
        with pytest.raises(ValueError, match="RECRAFT_API_KEY"):
            generate_image("prompt", out)
