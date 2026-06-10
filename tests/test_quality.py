from shorts_bot.drafts.quality import run_quality_checks


def test_quality_rejects_slop():
    report = run_quality_checks(
        topic="focus",
        hook="x",
        script="In today's fast-paced world you need focus.",
        help_angle="Helps students focus better during study sessions.",
    )
    assert not report.passed
    assert any("Slop" in issue for issue in report.issues)


def test_quality_warns_tagline_outro():
    report = run_quality_checks(
        topic="sleep",
        hook="I wake at 3am every night.",
        script=(
            "I wake at 3am and my brain won't stop. "
            "Phone stays dark, one breath, name the thought. "
            "You're still here. Good."
        ),
        help_angle="Helps night owls shorten the 3am spiral with one pre-sleep reset.",
    )
    assert any("tagline" in w.lower() for w in report.warnings)


def test_quality_passes_solid_draft():
    report = run_quality_checks(
        topic="focus",
        hook="Your brain isn't lazy — your setup is.",
        script=(
            "Your brain isn't lazy — your setup is. "
            "Before you study, clear one surface, set a 10-minute timer, and put your phone in another room. "
            "Pick one task, start ugly, and let momentum do the rest instead of waiting for perfect focus. "
            "One small reset beats another hour of fake productivity."
        ),
        help_angle="Helps overwhelmed students start focused study without relying on motivation.",
    )
    assert report.passed
