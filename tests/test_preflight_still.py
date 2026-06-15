"""Preflight peak still — gate before full Blender animation."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from shorts_bot.config import Settings
from shorts_bot.production.blender.preflight import PreflightFailedError, run_preflight_gate
from shorts_bot.production.vision_qc import run_preflight_still_qc


def test_run_preflight_still_qc_fails_dark_frame(tmp_path, monkeypatch):
    pack = tmp_path / "draft_2"
    pack.mkdir()
    (pack / "creature_lunge_lab.json").write_text('{"creature_only": true}', encoding="utf-8")
    still = pack / "preflight" / "peak_still.jpg"
    still.parent.mkdir(parents=True)
    still.write_bytes(b"tiny")

    fake = Settings(
        vision_qc_enabled=True,
        vision_qc_blocks_upload=True,
        blender_preflight_min_score=6.5,
        has_gemini=True,
    )
    monkeypatch.setattr("shorts_bot.production.vision_qc.settings", fake)

    with patch("shorts_bot.production.vision_qc._local_frame_checks", return_value=(["frame extract failed"], [], False)):
        report = run_preflight_still_qc(still, pack, topic="lunge", hook="face")

    assert report.passed is False
    assert (pack / "preflight" / "preflight_qc.json").is_file()


def test_run_preflight_still_qc_gemini_pass(tmp_path, monkeypatch):
    pack = tmp_path / "draft_2"
    pack.mkdir()
    (pack / "creature_lunge_lab.json").write_text('{"creature_only": true}', encoding="utf-8")
    still = pack / "preflight" / "peak_still.jpg"
    still.parent.mkdir(parents=True)
    still.write_bytes(b"\xff" * 2000)

    fake = Settings(
        vision_qc_enabled=True,
        vision_qc_blocks_upload=True,
        blender_preflight_min_score=6.5,
        micro_jumpscare_seconds=3.0,
        has_gemini=True,
    )
    monkeypatch.setattr("shorts_bot.production.vision_qc.settings", fake)

    with (
        patch("shorts_bot.production.vision_qc._local_frame_checks", return_value=([], [], True)),
        patch(
            "shorts_bot.production.vision_qc._gemini_vision_review",
            return_value={
                "score": 8.0,
                "pass": True,
                "issues": [],
                "warnings": [],
                "scare_potential": True,
            },
        ),
    ):
        report = run_preflight_still_qc(still, pack, topic="lunge", hook="face")

    assert report.passed is True
    assert report.score == 8.0


def test_preflight_gate_skipped_when_disabled(tmp_path, monkeypatch):
    fake = Settings(blender_preflight_still_enabled=False)
    monkeypatch.setattr("shorts_bot.production.blender.preflight.settings", fake)
    result = run_preflight_gate(2, tmp_path / "draft_2")
    assert result.skipped is True
    assert result.passed is True


def test_preflight_failed_error_carries_result():
    from shorts_bot.production.blender.preflight import PreflightResult

    pf = PreflightResult(passed=False, score=2.0, still_path=Path("/tmp/x.jpg"), message="bad framing")
    err = PreflightFailedError(pf)
    assert err.result.score == 2.0
    assert "bad framing" in str(err)
