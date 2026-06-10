from pathlib import Path

from shorts_bot.brand.assets import generate_banner_image, generate_profile_image


def test_generate_brand_pngs(tmp_path: Path):
    profile = generate_profile_image(tmp_path / "profile.png")
    banner = generate_banner_image(tmp_path / "banner.png")
    assert profile.stat().st_size > 500
    assert banner.stat().st_size > 2000


def test_youtube_copy_series_field():
    from shorts_bot.brand.loader import ChannelBrand

    fields = ChannelBrand().youtube_fields()
    assert fields.series == "The Minute Before"
    assert "Minute Before" in fields.description
