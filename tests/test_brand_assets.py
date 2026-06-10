from pathlib import Path

from shorts_bot.brand.assets import generate_banner_image, generate_profile_image


def test_generate_brand_pngs(tmp_path: Path):
    profile = generate_profile_image(tmp_path / "profile.png")
    banner = generate_banner_image(tmp_path / "banner.png")
    assert profile.stat().st_size > 500
    assert banner.stat().st_size > 2000
