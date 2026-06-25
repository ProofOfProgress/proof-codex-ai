from pathlib import Path

from shorts_bot.production.research import ProductionResearch, deep_research_topic, load_research


def test_offline_research_caches(tmp_path: Path, monkeypatch):
    from shorts_bot.config import Settings

    fake = Settings(data_dir=tmp_path, database_path=tmp_path / "t.db")
    monkeypatch.setattr("shorts_bot.config.settings", fake)
    monkeypatch.setattr("shorts_bot.production.research.settings", fake)
    monkeypatch.setattr("shorts_bot.llm.provider.get_llm_backend", lambda: None)

    r = deep_research_topic("the minute before a hard conversation")
    assert r.viewer_moment
    assert "Jenny" in " ".join(r.jenny_citations)
    assert load_research(r.topic) is not None


def test_research_draft_context_includes_beats():
    r = ProductionResearch(
        topic="test",
        niche="niche",
        viewer_moment="before talk",
        emotional_stakes="regret",
        hook_angles=["hook one"],
        script_beats=["beat one", "beat two"],
        visual_framing="upper 60%",
        competitor_gap="gap",
        title_formula="title",
    )
    ctx = r.draft_context()
    assert "before talk" in ctx
    assert "beat one" in ctx
