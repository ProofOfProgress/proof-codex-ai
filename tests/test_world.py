from shorts_bot.brand.loader import ChannelBrand
from shorts_bot.drafts.generator import SYSTEM_PROMPT
from shorts_bot.production.niche import (
    DEFAULT_TOPICS,
    NICHE_NAME,
    NICHE_POSITIONING,
    NICHE_TAGLINE,
    quality_lessons,
)
from shorts_bot.production.world import world_doc_path


def test_world_doc_exists():
    assert world_doc_path().exists()


def test_niche_positioning_ai_tech():
    assert "AI" in NICHE_POSITIONING
    assert "InVideo" in NICHE_POSITIONING or "twin" in NICHE_POSITIONING.lower()


def test_niche_default_topics_non_empty():
    assert len(DEFAULT_TOPICS) >= 10
    assert any("AI" in t or "ChatGPT" in t for t in DEFAULT_TOPICS)


def test_niche_constants():
    assert NICHE_NAME
    assert NICHE_TAGLINE


def test_generator_system_prompt_ai_tech():
    assert "AI" in SYSTEM_PROMPT or "tech" in SYSTEM_PROMPT.lower()
    assert "verdict" in SYSTEM_PROMPT.lower() or "takeaway" in SYSTEM_PROMPT.lower()
    assert "worship" not in SYSTEM_PROMPT.lower()


def test_brand_loader_draft_instructions():
    brand = ChannelBrand()
    instructions = brand.draft_instructions()
    assert instructions


def test_quality_lessons():
    assert "Better:" in quality_lessons()
