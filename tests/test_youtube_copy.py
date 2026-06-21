from shorts_bot.brand.loader import ChannelBrand
from shorts_bot.brand.youtube_copy import parse_youtube_copy


SAMPLE = """CHANNEL NAME: Soft Continuity

DESCRIPTION:
Small fixes for heavy days.

Calm, faceless Shorts.

TAGLINE: you're still here. good.

PINNED COMMENT: Which topic next?
"""


def test_parse_youtube_copy_fields():
    fields = parse_youtube_copy(SAMPLE)
    assert fields.channel_name == "Soft Continuity"
    assert "Small fixes for heavy days" in fields.description
    assert "Calm, faceless Shorts" in fields.description
    assert fields.tagline == "you're still here. good."
    assert fields.pinned_comment == "Which topic next?"


def test_brand_loader_youtube_fields():
    brand = ChannelBrand()
    fields = brand.youtube_fields()
    assert fields.channel_name
    assert "ai" in fields.keywords.lower() or "tech" in fields.keywords.lower()


def test_parse_empty_copy():
    fields = parse_youtube_copy("")
    assert fields.channel_name == ""
    assert fields.description == ""
