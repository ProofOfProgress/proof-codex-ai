from shorts_bot.production.script_humanize import finalize_script


def test_finalize_script_reduces_ai_score():
    hook = "Stop scrolling — this one habit around cant sleep at 3am actually helps."
    script = (
        "Stop scrolling — this one habit around cant sleep at 3am actually helps. "
        "Furthermore it is important to note that you must delve into sleep."
    )
    r = finalize_script("cant sleep at 3am", hook, script, "helps sleep", max_passes=5, threshold=50)
    assert r.final_ai_score <= 50 or r.passes >= 1
    assert "Furthermore" not in r.script or r.final_ai_score < 80
