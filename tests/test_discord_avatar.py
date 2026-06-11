from pathlib import Path


def test_resolve_avatar_path(tmp_path: Path, monkeypatch):
    from shorts_bot.config import Settings
    from shorts_bot.discord_bot.avatar import _avatar_bytes, resolve_avatar_path

    img = tmp_path / "bot.png"
    from PIL import Image

    Image.new("RGB", (400, 300), "#112233").save(img)

    fake = Settings(discord_avatar_path=img)
    monkeypatch.setattr("shorts_bot.discord_bot.avatar.settings", fake)

    assert resolve_avatar_path() == img.resolve()
    data = _avatar_bytes(img)
    assert len(data) > 100
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
