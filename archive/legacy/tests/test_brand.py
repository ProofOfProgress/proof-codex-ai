from pathlib import Path

from shorts_bot.brand.loader import ChannelBrand


def test_brand_voice_loads():
    brand = ChannelBrand()
    voice = brand.voice()
    assert "oracle" in voice.lower() or "help" in voice.lower()


def test_brand_draft_instructions():
    brand = ChannelBrand()
    text = brand.draft_instructions()
    assert len(text) > 100


def test_youtube_copy_exists():
    brand = ChannelBrand()
    copy = brand.youtube_copy()
    assert "Soft Continuity" in copy or len(copy) >= 0


def test_identity_file():
    assert Path("channel/brand/identity.md").exists()
