# Tests for B2B outreach humanization

from shorts_bot.b2b.outreach import BANNED_PHRASES, draft_outreach, score_outreach


def test_banned_phrases_flagged():
    text = "I hope this email finds you well. I'd love to pick your brain about synergy."
    _, issues = score_outreach(text, channel="email")
    assert any("banned" in i for i in issues)


def test_offline_dm_sounds_human():
    r = draft_outreach(
        company="Acme AI",
        product="Acme Writer",
        detail="your Product Hunt launch yesterday",
        channel="dm",
    )
    assert r.body
    assert "acme" in r.body.lower()
    assert r.ai_score <= 40
    assert not any(p in r.body.lower() for p in BANNED_PHRASES[:5])


def test_offline_email_has_subject():
    r = draft_outreach(
        company="TestCo",
        product="TestBot",
        detail="the new pricing page",
        channel="email",
    )
    assert r.subject
    assert "TestBot" in r.subject or "TestBot" in r.body
