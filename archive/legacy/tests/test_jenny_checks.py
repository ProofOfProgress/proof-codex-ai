from shorts_bot.production.jenny_checks import check_jenny_voice


def test_second_person_passes():
    assert not check_jenny_voice(
        "You checked the locks twice. The hallway feed was empty.",
        "Your security camera flagged motion at 3:12 AM.",
    )


def test_missing_you_fails():
    issues = check_jenny_voice("The hallway was empty.", "Motion alert.")
    assert any("second-person" in i.lower() for i in issues)


def test_plural_fails():
    issues = check_jenny_voice("Hey guys, here's a tip for everyone.", "Hook")
    assert any("singular" in i.lower() or "Plural" in i for i in issues)
