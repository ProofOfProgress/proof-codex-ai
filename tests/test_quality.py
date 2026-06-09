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
