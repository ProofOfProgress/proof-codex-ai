"""Tests for bubble batch generation."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from shorts_bot.tiktok_shop import bubble_batch
from shorts_bot.tiktok_shop.bubble_wrap import BubbleWrapResult


def test_resolve_subjects_default_count():
    subs = bubble_batch.resolve_subjects(count=10, subjects=None)
    assert len(subs) == 10
    assert subs[0] == "frog"


def test_resolve_subjects_custom_list():
    subs = bubble_batch.resolve_subjects(count=3, subjects=["cat", "dog", "fish"])
    assert subs == ["cat", "dog", "fish"]


def test_run_bubble_batch_writes_manifest(tmp_path, monkeypatch):
    slides_root = tmp_path / "bubble_wrap" / "slides"
    slides_root.mkdir(parents=True)
    batches_root = tmp_path / "bubble_wrap" / "batches"
    batches_root.mkdir(parents=True)

    def fake_generate(*, subject: str, account: str, preview: bool, force: bool) -> BubbleWrapResult:
        out = slides_root / account
        out.mkdir(parents=True, exist_ok=True)
        s1 = out / "slide1_hook.jpg"
        s2 = out / "slide2_cta.jpg"
        s1.write_bytes(b"j1")
        s2.write_bytes(b"j2")
        return BubbleWrapResult(subject, f"{subject.upper()} HOOK", s1, s2, None, "mock")

    monkeypatch.setattr(bubble_batch, "batch_output_root", lambda: batches_root)
    monkeypatch.setattr(bubble_batch, "generate_bubble_wrap_slides", fake_generate)

    result = bubble_batch.run_bubble_batch(count=2, subjects=["frog", "duck"], force=True, preview=False)
    assert result.succeeded == 2
    assert result.manifest_path.is_file()
    data = result.manifest_path.read_text(encoding="utf-8")
    assert "store_only" in data
    assert "frog" in data
