# Tests for TikTok Shop image parsing + Kling client helpers

import json
from unittest.mock import MagicMock, patch

import httpx

from shorts_bot.tiktok_shop import kling_client
from shorts_bot.tiktok_shop.product_images import download_cover, parse_cover_url
from shorts_bot.tiktok_shop.product_scout import enrich_cover_urls


def test_parse_cover_url_json_list():
    raw = json.dumps([{"url": "https://cdn.example/a.jpg", "index": 0}])
    assert parse_cover_url(raw) == "https://cdn.example/a.jpg"


def test_parse_cover_url_plain():
    assert parse_cover_url("https://cdn.example/b.png") == "https://cdn.example/b.png"


def test_parse_cover_url_empty():
    assert parse_cover_url("") == ""
    assert parse_cover_url(None) == ""


def test_tiktok_cdn_from_sale_props():
    from shorts_bot.tiktok_shop.product_images import tiktok_cdn_url_from_detail

    row = {
        "sale_props": json.dumps(
            [
                {
                    "prop_name": "Color",
                    "sale_prop_values": [
                        {"image": "https://p16-oec-general-useast5.ttcdn-us.com/foo.webp"},
                    ],
                }
            ]
        )
    }
    assert "ttcdn-us.com" in tiktok_cdn_url_from_detail(row)


def test_suggest_style_beauty_vs_shirt():
    from shorts_bot.tiktok_shop.render import NEGATIVE_PROMPT, prompt_for_style, suggest_style

    assert suggest_style("Speak Love Lip Balm") == "vanity"
    assert suggest_style("Funny Dog Mom Shirt") == "lifestyle"
    assert suggest_style("Random Gadget") == "studio"
    assert "marble vanity" in prompt_for_style("vanity", product_name="x")
    assert "void" in NEGATIVE_PROMPT


def test_kling_create_image2video_sends_negative_prompt(monkeypatch):
    captured: dict = {}

    class FakeResponse:
        status_code = 200

        @staticmethod
        def json():
            return {"code": 0, "data": {"task_id": "task-999"}}

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def post(self, url, headers, json):
            captured["json"] = json
            return FakeResponse()

    monkeypatch.setattr("shorts_bot.tiktok_shop.kling_client.httpx.Client", FakeClient)
    monkeypatch.setattr(
        "shorts_bot.tiktok_shop.kling_client._auth_header",
        lambda: {"Authorization": "Bearer test"},
    )

    task_id = kling_client.create_image2video(
        image_url="https://example.com/p.jpg",
        prompt="product on shelf",
        negative_prompt="empty void, gray background",
    )
    assert task_id == "task-999"
    assert captured["json"]["negative_prompt"] == "empty void, gray background"


def test_prepare_vertical_9x16():
    from io import BytesIO

    from PIL import Image

    from shorts_bot.tiktok_shop.product_images import prepare_vertical_9x16, _FIT_PAD_RGB

    square = Image.new("RGB", (1000, 1000), color=(255, 0, 0))
    buf = BytesIO()
    square.save(buf, format="JPEG")
    out = prepare_vertical_9x16(buf.getvalue(), width=1080, height=1920, fit_scale=0.88)
    result = Image.open(BytesIO(out))
    assert result.size == (1080, 1920)
    # Zoom-out fit: corners are padding gray, not product red
    assert result.getpixel((0, 0)) == _FIT_PAD_RGB
    assert result.getpixel((0, 0)) != (255, 0, 0)


def test_wrap_on_screen_caption():
    from shorts_bot.tiktok_shop.video_editor import wrap_on_screen_caption

    wrapped = wrap_on_screen_caption(
        "Tired of cheap watches that scratch the second you bump them on the door frame"
    )
    assert "\n" in wrapped
    assert len(wrapped.splitlines()) >= 2


def test_burn_on_screen_caption(tmp_path):
    import shutil

    if not shutil.which("ffmpeg"):
        import pytest

        pytest.skip("ffmpeg not installed")

    from shorts_bot.tiktok_shop.video_editor import burn_on_screen_caption

    # Tiny synthetic clip — ffmpeg required
    src = tmp_path / "src.mp4"
    subprocess = __import__("subprocess")
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "color=c=gray:s=540x960:d=1",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(src),
        ],
        check=True,
        capture_output=True,
    )
    dest = tmp_path / "out.mp4"
    burn_on_screen_caption(src, dest, "Reminder for the folks who hate scratched screens")
    assert dest.is_file() and dest.stat().st_size > 1000


def test_download_cover_skips_on_403(tmp_path, monkeypatch):
    fake_settings = type("S", (), {"data_dir": tmp_path})()
    monkeypatch.setattr("shorts_bot.tiktok_shop.product_images.settings", fake_settings)

    response = MagicMock()
    response.status_code = 403
    response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "403",
        request=MagicMock(),
        response=response,
    )

    with patch("shorts_bot.tiktok_shop.product_images.httpx.Client") as client_cls:
        client = MagicMock()
        client.__enter__.return_value = client
        client.get.return_value = response
        client_cls.return_value = client

        result = download_cover(
            product_id="123",
            cover_url="https://cdn.example/x.jpg",
        )

    assert result is None


def test_enrich_cover_urls_fills_missing(monkeypatch):
    rows = [{"product_id": "111", "cover_url": ""}]
    detail = [{"product_id": "111", "cover_url": '[{"url":"https://cdn.example/z.jpg","index":0}]'}]

    monkeypatch.setattr(
        "shorts_bot.tiktok_shop.product_scout.echotik_client.configured",
        lambda: True,
    )
    monkeypatch.setattr(
        "shorts_bot.tiktok_shop.product_scout.echotik_client.product_detail",
        lambda ids: detail,
    )

    out = enrich_cover_urls(rows)
    assert out[0]["cover_url"] == "https://cdn.example/z.jpg"


def test_kling_task_id_from_data():
    body = {"data": {"task_id": "abc-123"}}
    assert kling_client._task_id(body) == "abc-123"


def test_kling_video_url_from_nested_result():
    body = {
        "data": {
            "task_result": {
                "videos": [{"url": "https://video.example/out.mp4"}],
            }
        }
    }
    assert kling_client._video_url(body) == "https://video.example/out.mp4"


def test_kling_configured_with_api_key(monkeypatch):
    class FakeSettings:
        kling_api_key = "api-key-kling-test"
        kling_access_key = ""
        kling_secret_key = ""

        @property
        def has_kling_official(self) -> bool:
            return bool(self.kling_api_key)

    monkeypatch.setattr("shorts_bot.tiktok_shop.kling_client.settings", FakeSettings())
    assert kling_client.configured() is True
