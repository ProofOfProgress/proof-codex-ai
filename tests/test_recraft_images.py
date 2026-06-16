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
        recraft_style_id_horror="11111111-2222-3333-4444-555555555555",
    )
    out = tmp_path / "out.png"

    with patch("shorts_bot.production.images.router.settings", fake):
        with patch(
            "shorts_bot.production.images.router.generate_recraft_image",
            return_value="recraft/recraftv3",
        ) as gen:
            assert generate_image("prompt", out) == "recraft/recraftv3"
            gen.assert_called_once()
            assert gen.call_args.kwargs["style_id"] == "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"

            gen.reset_mock()
            assert generate_image("prompt", out, style_id="11111111-2222-3333-4444-555555555555") == "recraft/recraftv3"
            assert gen.call_args.kwargs["style_id"] == "11111111-2222-3333-4444-555555555555"

    missing = Settings(image_provider="recraft", recraft_api_key=None)
    with patch("shorts_bot.production.images.router.settings", missing):
        with pytest.raises(ValueError, match="RECRAFT_API_KEY"):
            generate_image("prompt", out)


def test_recraft_style_routing_comedy_vs_horror(monkeypatch):
    from shorts_bot.config import Settings
    from shorts_bot.production.image_prompts import (
        build_image_briefs,
        classify_lost_boy_shot,
        recraft_style_id_for_segment_text,
        segment_is_horror_snap,
    )
    from shorts_bot.production.turboscribe_parser import TranscriptSegment

    fake = Settings(
        image_provider="recraft",
        recraft_style_id="522c040d-88f1-47fa-a604-406dfea1a129",
        recraft_style_id_horror="d1155936-62d4-42f0-a8f7-f09442e8701c",
    )
    monkeypatch.setattr("shorts_bot.config.settings", fake)

    assert segment_is_horror_snap("Super chill day.") is False
    assert segment_is_horror_snap("Don't look left.") is True
    assert recraft_style_id_for_segment_text("Super chill day.", topic="forest") == "522c040d-88f1-47fa-a604-406dfea1a129"
    assert recraft_style_id_for_segment_text("Those aren't arms.", topic="forest") == "d1155936-62d4-42f0-a8f7-f09442e8701c"

    assert classify_lost_boy_shot("He waved.") == "boy_waving_group"
    assert classify_lost_boy_shot("Between the pines, a small boy.") == "boy_reveal"
    # Group wave uses comedy style so hikers + boy appear together
    assert (
        recraft_style_id_for_segment_text("He waved.", topic="the lost boy in the woods")
        == "522c040d-88f1-47fa-a604-406dfea1a129"
    )
    assert (
        recraft_style_id_for_segment_text("His smile didn't move.", topic="the lost boy in the woods")
        == "d1155936-62d4-42f0-a8f7-f09442e8701c"
    )

    segs = [
        TranscriptSegment(0.0, "Peaceful morning.", "00.00"),
        TranscriptSegment(13.0, "He waved.", "00.13"),
    ]
    briefs = build_image_briefs(segs, topic="the lost boy in the woods")
    assert briefs[0].recraft_style_id == "522c040d-88f1-47fa-a604-406dfea1a129"
    assert briefs[1].recraft_style_id == "522c040d-88f1-47fa-a604-406dfea1a129"
    assert "ARM RAISED" in briefs[1].prompt or "waving" in briefs[1].prompt.lower()
