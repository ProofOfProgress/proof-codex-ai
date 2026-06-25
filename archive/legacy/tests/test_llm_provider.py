from unittest.mock import patch

from shorts_bot.llm.provider import get_llm_backend, has_full_chat


def test_prefers_gemini_over_openai():
    with patch("shorts_bot.llm.provider.settings") as s:
        s.has_gemini = True
        s.has_openai = True
        s.gemini_api_key = "a" * 32
        s.gemini_model = "gemini-2.0-flash"
        backend = get_llm_backend()
        assert backend is not None
        assert backend.provider == "gemini"
        assert backend.model == "gemini-2.0-flash"


def test_offline_when_no_keys():
    with patch("shorts_bot.llm.provider.settings") as s:
        s.has_gemini = False
        s.has_openai = False
        assert get_llm_backend() is None
        assert has_full_chat() is False
