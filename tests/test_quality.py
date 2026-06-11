from shorts_bot.drafts.quality import run_quality_checks


def test_quality_rejects_slop():
    report = run_quality_checks(
        topic="mirror blink",
        hook="Something scary happened.",
        script="In today's fast-paced world you hear scary stories about mirrors.",
        help_angle="Generic ghost story for anyone who likes horror.",
    )
    assert not report.passed
    assert any("Slop" in issue for issue in report.issues)


def test_quality_rejects_cosy_tone():
    report = run_quality_checks(
        topic="sleep",
        hook="You wake at 3am every night.",
        script=(
            "You wake at 3am and your brain won't stop. "
            "Try one breath and a cosy self-care protocol before bed. "
            "You told yourself it was nothing. "
            "You turned — the closet door opened behind you."
        ),
        help_angle="Reflection scare — mirror blink timing is impossible.",
    )
    assert not report.passed
    assert any("cosy" in issue.lower() or "self-help" in issue.lower() for issue in report.issues)


def test_quality_passes_solid_horror_draft():
    report = run_quality_checks(
        topic="mirror blink",
        hook="You blinked at the mirror — your reflection blinked one second later.",
        script=(
            "You blinked at the mirror — your reflection blinked one second later. "
            "You stepped closer and the glass stayed still, but the eyes in it didn't. "
            "You raised your phone to record proof and the screen showed an empty bathroom. "
            "You looked up — the reflection was already facing the door behind you. "
            "The hallway light flickered off. "
            "You told yourself it was a lag, a trick of tired eyes. "
            "You turned to leave — and the thing in the mirror opened its mouth."
        ),
        help_angle="Wrong-reflection jumpscare — delayed blink is physically impossible.",
    )
    assert report.passed
