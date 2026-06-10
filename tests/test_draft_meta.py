from shorts_bot.drafts.meta import load_draft_meta, save_draft_meta, visual_beats_for_draft


def test_visual_beats_roundtrip(tmp_path, monkeypatch):
    from shorts_bot.config import Settings

    fake = Settings(data_dir=tmp_path)
    monkeypatch.setattr("shorts_bot.drafts.meta.settings", fake)

    save_draft_meta(42, visual_beats=["bathroom stall", "deep breath"])
    assert visual_beats_for_draft(42) == ["bathroom stall", "deep breath"]
    assert load_draft_meta(42)["visual_beats"][0] == "bathroom stall"
