from shorts_bot.production.jenny_checks import check_jenny_voice


def test_first_person_passes():
    assert not check_jenny_voice("I used to grab my phone at 3am.", "I can't sleep")


def test_plural_fails():
    issues = check_jenny_voice("Hey guys, here's a tip for everyone.", "Hook")
    assert any("singular" in i.lower() or "Plural" in i for i in issues)
