"""Tests for Gemini model routing and retry helper."""

from unittest.mock import patch

import pytest

from shorts_bot.llm import gemini_utils


def test_vision_model_defaults_to_flash():
    with patch.object(gemini_utils.settings, "gemini_vision_model", ""):
        assert gemini_utils.vision_model() == gemini_utils.DEFAULT_VISION_MODEL


def test_vision_model_respects_override():
    with patch.object(gemini_utils.settings, "gemini_vision_model", "gemini-2.5-pro"):
        assert gemini_utils.vision_model() == "gemini-2.5-pro"


def test_cheap_model_uses_settings():
    with patch.object(gemini_utils.settings, "gemini_model", "gemini-2.5-flash-lite"):
        assert gemini_utils.cheap_model() == "gemini-2.5-flash-lite"


def test_call_with_retry_succeeds_after_transient():
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] < 2:
            raise RuntimeError("503 Service Unavailable")
        return "ok"

    with patch("shorts_bot.llm.gemini_utils.time.sleep"):
        assert gemini_utils.call_with_retry(flaky, max_attempts=3) == "ok"
    assert calls["n"] == 2


def test_call_with_retry_raises_non_retryable():
    def boom():
        raise ValueError("bad json")

    with pytest.raises(ValueError, match="bad json"):
        gemini_utils.call_with_retry(boom, max_attempts=3)


def test_visual_critic_context_includes_coach_rules():
    text = gemini_utils.visual_critic_context(max_chars=5000)
    assert "micro-shake" in text.lower()
    assert "parallax" in text.lower()
