from pathlib import Path
from unittest.mock import MagicMock, patch

from shorts_bot.production.research import ProductionResearch, deep_research_topic, load_research
from shorts_bot.production.upload_meta import build_upload_package
from shorts_bot.research.vidiq import VidIQKeyword, VidIQResult, _parse_keyword_rows
from shorts_bot.research.web_gather import WebGatherResult, WebSnippet
from shorts_bot.services.chat_router import parse_research_request


def test_parse_research_request_deep():
    assert parse_research_request("deep research hard conversation") == ("hard conversation", True)
    assert parse_research_request("research sleep anxiety") == ("sleep anxiety", False)
    assert parse_research_request("research refresh topic") == ("topic", True)


def test_vidiq_parse_keyword_rows():
    text = "keyword one\t1000\tlow\t72\nkeyword two\t500\tmed\t55"
    rows = _parse_keyword_rows(text)
    assert len(rows) >= 1
    assert rows[0].keyword


def test_upload_meta_uses_research_title():
    r = ProductionResearch(
        topic="hard talk",
        niche="n",
        viewer_moment="m",
        emotional_stakes="s",
        hook_angles=[],
        script_beats=[],
        visual_framing="f",
        competitor_gap="g",
        title_formula="Before the hard talk — breathe once #Shorts",
        keyword_insights=[{"keyword": "anxiety before meeting", "volume": "1k", "competition": "low"}],
    )
    pkg = build_upload_package("hard talk", "hook", draft_id=1, research=r)
    assert "hard talk" in pkg.title.lower() or "Before" in pkg.title
    assert "anxiety before meeting" in pkg.tags


def test_deep_research_with_mocked_web(tmp_path: Path, monkeypatch):
    from shorts_bot.config import Settings

    fake = Settings(data_dir=tmp_path, database_path=tmp_path / "t.db")
    monkeypatch.setattr("shorts_bot.config.settings", fake)
    monkeypatch.setattr("shorts_bot.production.research.settings", fake)

    web = WebGatherResult(
        topic="test topic",
        queries=["test topic"],
        snippets=[WebSnippet(title="Article", url="https://example.com", snippet="Useful tip", source="web")],
        youtube_suggestions=["test topic shorts"],
    )

    monkeypatch.setattr("shorts_bot.llm.provider.get_llm_backend", lambda: None)
    monkeypatch.setattr(
        "shorts_bot.production.research._gather_external_context",
        lambda topic: {
            "web_context": web.context_block(),
            "competitor_context": "- Competitor title",
            "keyword_context": "vol=high",
            "web_sources": [{"title": "Article", "url": "https://example.com", "snippet": "x", "source": "web"}],
            "competitor_titles": ["Competitor title"],
            "keyword_insights": [{"keyword": "test kw", "volume": "1k", "competition": "low", "score": ""}],
            "search_queries": ["test topic"],
            "research_sources": ["web_search", "youtube_api"],
        },
    )

    r = deep_research_topic("test topic", force_refresh=True)
    assert r.viewer_moment
    assert "web_search" in r.research_sources or "offline" in r.research_sources
    assert load_research("test topic") is not None


def test_vidiq_context_block():
    r = VidIQResult(
        topic="sleep",
        keywords=[VidIQKeyword(keyword="cant sleep", search_volume="10k", competition="low", overall_score="80")],
        source="vidiq_browser",
    )
    block = r.context_block()
    assert "cant sleep" in block
    assert "10k" in block
