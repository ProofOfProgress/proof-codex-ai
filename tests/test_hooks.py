"""Tests for Jenny hook templates and weak-hook detection."""

from shorts_bot.production.hooks import (
    HOOK_TEMPLATES,
    hook_for_product,
    migrate_verdict_hint,
    score_hook,
)


def test_curated_hook_not_weak():
    hook = hook_for_product("ChatGPT Plus")
    score, issues = score_hook(hook)
    assert score >= 7.0
    assert not issues


def test_weak_is_worth_it_hook_fails():
    score, issues = score_hook("Is ChatGPT Plus worth it?")
    assert score < 7.0
    assert issues


def test_weak_everyone_paying_fails():
    score, issues = score_hook("Everyone's paying for ChatGPT Plus — I tested if it's worth it.")
    assert score < 7.0


def test_migrate_verdict_to_weakness():
    s, w = migrate_verdict_hint("Skip unless you hit limits daily")
    assert w
    assert "Skip" not in w or "unless" in w


def test_hook_templates_no_worth_it():
    for tpl in HOOK_TEMPLATES:
        assert "worth it" not in tpl.lower()
