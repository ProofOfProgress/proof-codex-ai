"""Pipeline orchestration — prompt dispatch and validation."""

from pathlib import Path

from shorts_bot.tiktok_shop.pipeline import (
    dispatch_brief,
    save_prompt_file,
    validate_before_render,
)


def test_dispatch_brief_includes_reference_image(tmp_path):
    prod = tmp_path / "module4.jpg"
    ref = tmp_path / "ref.jpg"
    prod.write_bytes(b"x")
    ref.write_bytes(b"y")
    text = dispatch_brief(
        product_name="Insulated Tumbler",
        product_image=prod,
        reference_image=ref,
        mission_id="m-1",
    )
    assert "Insulated Tumbler" in text
    assert str(prod.resolve()) in text
    assert str(ref.resolve()) in text
    assert "Listing/reference photo" in text
    assert "NOT plain white box" in text


def test_validate_before_render_requires_prompt(tmp_path):
    img = tmp_path / "p.jpg"
    img.write_bytes(b"fake")
    check = validate_before_render(product_name="X", product_image=img, prompt_text="")
    assert not check.ok
    assert any("prompt" in e.lower() for e in check.errors)


def test_save_prompt_file(tmp_path, monkeypatch):
    class FakeSettings:
        data_dir = tmp_path

    monkeypatch.setattr("shorts_bot.tiktok_shop.pipeline.settings", FakeSettings())
    path = save_prompt_file(product_name="Test Product", prompt="Use uploaded image as exact reference.")
    assert path.is_file()
    assert "exact reference" in path.read_text(encoding="utf-8")
