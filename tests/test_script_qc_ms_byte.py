from unittest.mock import patch

from shorts_bot.invideo.shop_brief import shop_brief
from shorts_bot.learning.script_qc import _offline_qc, score_script_brief


def test_script_qc_shop_format_passes_offline():
    brief = shop_brief(
        product="Jar Grip Opener",
        hook="Jar lid won't budge? This grip tool pops it open in three seconds.",
        weakness_hint="Stuck lids ruin cooking flow.",
        strength_hint="Rubber grip pops lid with leverage.",
        verdict_hint="Linked in the orange cart.",
    )
    qc = _offline_qc(
        product="Jar Grip Opener",
        hook="Jar lid won't budge? This grip tool pops it open in three seconds.",
        brief=brief,
        verdict_hint="",
    )
    assert qc.score >= 7.0
    assert qc.passed
    assert not any("Pay/Skip/Wait" in i for i in qc.issues)


def test_script_qc_penalizes_pay_skip_wait():
    bad = "Review gadget. Verdict: Pay if you cook daily. Skip otherwise."
    qc = _offline_qc(
        product="Jar Grip Opener",
        hook="Is this worth it?",
        brief=bad,
        verdict_hint="Pay or Skip",
    )
    assert any("Pay/Skip/Wait" in i for i in qc.issues)


def test_script_qc_integration_respects_disabled():
    with patch("shorts_bot.learning.script_qc.settings") as mock_settings:
        mock_settings.script_qc_enabled = False
        qc = score_script_brief(product="X", hook="bad", brief="bad")
        assert qc.passed
