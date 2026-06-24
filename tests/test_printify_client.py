# Tests for Printify client helpers

from unittest.mock import patch

from shorts_bot.tiktok_shop import printify_client


def test_configured_with_token(monkeypatch):
    fake = type("S", (), {"printify_api_token": "real-token-abc", "printify_shop_id": ""})()
    monkeypatch.setattr("shorts_bot.tiktok_shop.printify_client.settings", fake)
    assert printify_client.configured() is True


def test_hero_image_prefers_front():
    product = {
        "images": [
            {"src": "https://cdn.example/back.jpg", "position": "back"},
            {"src": "https://cdn.example/front.jpg", "position": "front"},
        ]
    }
    assert printify_client.hero_image_url(product) == "https://cdn.example/front.jpg"


def test_sync_products_writes_cache(tmp_path, monkeypatch):
    fake_settings = type("S", (), {"data_dir": tmp_path, "printify_api_token": "x", "printify_shop_id": "1"})()
    monkeypatch.setattr("shorts_bot.tiktok_shop.printify_client.settings", fake_settings)

    sample = [{"id": "99", "title": "Funny Dog Mom Tee", "images": [{"src": "https://cdn/x.jpg", "position": "front"}], "visible": True, "tags": []}]

    with patch("shorts_bot.tiktok_shop.printify_client.list_products", return_value=sample):
        path = printify_client.sync_products(shop_id="1")

    assert path.is_file()
    rows = printify_client.load_cached_products()
    assert rows[0]["title"] == "Funny Dog Mom Tee"
    assert rows[0]["hero_image"].startswith("https://")
