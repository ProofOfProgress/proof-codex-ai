# Tests — operating tips + pre-publish gate

from pathlib import Path

from shorts_bot.operating.tips import load_tips, code_tips_for
from shorts_bot.tiktok_shop.pre_publish_gate import run_pre_publish_gate


def test_load_operating_tips():
    tips = load_tips()
    assert len(tips) >= 5
    assert any(t.id == "T002" for t in tips)


def test_fast_carousel_gate_no_vision(tmp_path, monkeypatch):
    s1 = tmp_path / "hook.png"
    s2 = tmp_path / "cta.png"
    s1.write_bytes(b"x")
    s2.write_bytes(b"y")
    monkeypatch.setattr(
        "shorts_bot.config.settings.zernio_declare_aigc",
        True,
    )
    monkeypatch.setattr(
        "shorts_bot.config.settings.module1_vision_qc_enabled",
        False,
    )
    report = run_pre_publish_gate(
        "carousel",
        tier="fast",
        slide1=s1,
        slide2=s2,
        title="Duck ASMR",
        account_id="bubble_test",
    )
    assert report.passed
    assert report.vision_ran is False


def test_carousel_gate_blocks_bad_caption(tmp_path, monkeypatch):
    s1 = tmp_path / "hook.png"
    s2 = tmp_path / "cta.png"
    s1.write_bytes(b"x")
    s2.write_bytes(b"y")
    monkeypatch.setattr("shorts_bot.config.settings.module1_vision_qc_enabled", False)
    report = run_pre_publish_gate(
        "carousel",
        tier="fast",
        slide1=s1,
        slide2=s2,
        title="flash sale bubble wrap",
        account_id="bubble_test",
    )
    assert not report.passed
    assert any("flash sale" in v.lower() or "T006" in v for v in report.violations)


def test_code_tips_for_carousel():
    tips = code_tips_for("carousel")
    ids = {t.id for t in tips}
    assert "T004" in ids
