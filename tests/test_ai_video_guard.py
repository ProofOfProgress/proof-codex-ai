import pytest

from shorts_bot.config import settings
from shorts_bot.production.ai_video_guard import require_ai_video_generation


def test_regen_blocked_when_disabled(monkeypatch):
    monkeypatch.setattr(settings, "ai_video_generation_enabled", False)
    with pytest.raises(RuntimeError, match="disabled"):
        require_ai_video_generation(action="test")


def test_regen_allowed_when_enabled(monkeypatch):
    monkeypatch.setattr(settings, "ai_video_generation_enabled", True)
    require_ai_video_generation(action="test")
