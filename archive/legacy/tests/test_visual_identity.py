from shorts_bot.production.ai_video_prompts import visual_dna


def test_visual_dna_stub():
    assert "tech" in visual_dna().lower() or "review" in visual_dna().lower()
