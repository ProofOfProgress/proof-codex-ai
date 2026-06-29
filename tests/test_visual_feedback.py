"""Tests for Gemini visual feedback loop."""

from pathlib import Path
from unittest.mock import patch

from shorts_bot.tiktok_shop.visual_feedback import (
    VisualCritiqueReport,
    review_reference_image,
    review_video,
    suggest_prompt_revision,
)


def test_handoff_for_prompt_builder():
    report = VisualCritiqueReport(
        kind="video",
        product="Tumbler",
        score=4,
        good_enough=False,
        summary="Camera feels static.",
        prompt_fixes=["Emphasize slow arc left-to-right with handheld micro-shake"],
        prompt_used="Arc Camera Shot...",
    )
    text = report.handoff_for_prompt_builder()
    assert "Visual critic feedback" in text
    assert "Arc Camera Shot" in text
    assert "handheld micro-shake" in text


def test_review_reference_image_parses_gemini_json(tmp_path: Path, monkeypatch):
    img = tmp_path / "prod.jpg"
    img.write_bytes(b"\xff\xd8\xff" + b"x" * 100)

    def fake_gemini(**kwargs):
        return {
            "score": 8,
            "ready_for_kling": True,
            "good_enough": True,
            "summary": "Clean product on white.",
            "issues": [],
            "suggestions": [],
            "prompt_fixes": [],
        }

    monkeypatch.setattr("shorts_bot.tiktok_shop.visual_feedback._gemini_json", fake_gemini)
    report = review_reference_image(img, product="Tumbler")
    assert report.good_enough is True
    assert report.score == 8


def test_suggest_prompt_revision_returns_text(monkeypatch):
    critique = VisualCritiqueReport(
        kind="video",
        product="Tumbler",
        prompt_fixes=["Stronger arc motion"],
    )

    monkeypatch.setattr(
        "shorts_bot.tiktok_shop.visual_feedback._gemini_text",
        lambda **kwargs: "Use the uploaded product image. Slow arc with micro-shake.",
    )
    out = suggest_prompt_revision(
        original_prompt="Static studio shot.",
        critique=critique,
        product="Tumbler",
    )
    assert "arc" in out.lower()
