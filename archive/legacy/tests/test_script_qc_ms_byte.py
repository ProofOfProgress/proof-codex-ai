from unittest.mock import patch

from shorts_bot.learning.script_qc import _offline_qc, score_script_brief
from shorts_bot.invideo.ms_byte import ms_byte_brief


def test_script_qc_ms_byte_format_passes_offline():
    brief = ms_byte_brief(
        product="Claude Code",
        hook="Claude Code sounds free — until your Pro limits vanish.",
        strength_hint="Terminal agent edits repos fast.",
        weakness_hint="Heavy use burns Pro limits.",
    )
    qc = _offline_qc(
        product="Claude Code",
        hook="Claude Code sounds free — until your Pro limits vanish.",
        brief=brief,
        verdict_hint="",
    )
    assert qc.score >= 7.0
    assert qc.passed
    assert not any("Pay/Skip/Wait" in i for i in qc.issues)


def test_script_qc_flags_tts_x_as_word_offline():
    brief = ms_byte_brief(
        product="Grok",
        hook="Trends on X matter.",
        strength_hint="live X posts",
    )
    qc = _offline_qc(product="Grok", hook="Trends on X matter.", brief=brief, verdict_hint="")
    assert any("Twitter" in i or "TTS" in i for i in qc.issues)


def test_script_qc_penalizes_pay_skip_wait():
    bad = "Review ChatGPT. Verdict: Pay if you write daily. Skip otherwise."
    qc = _offline_qc(
        product="ChatGPT Plus",
        hook="Is ChatGPT worth it?",
        brief=bad,
        verdict_hint="Pay or Skip",
    )
    assert any("Pay/Skip/Wait" in i for i in qc.issues)


def test_script_qc_integration_respects_disabled():
    with patch("shorts_bot.learning.script_qc.settings") as mock_settings:
        mock_settings.script_qc_enabled = False
        qc = score_script_brief(product="X", hook="bad", brief="bad")
        assert qc.passed
