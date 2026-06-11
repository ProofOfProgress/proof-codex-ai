from shorts_bot.production.horror_repair import script_needs_horror_repair


def test_detects_first_person_drift():
    assert script_needs_horror_repair(
        "So, my security camera flagged motion. I live alone.",
        "My security camera flagged motion at 3 AM.",
    )


def test_second_person_ok():
    assert not script_needs_horror_repair(
        "You opened the app. The hallway was empty. You told yourself it was a glitch.",
        "Your security camera flagged motion at 3:12 AM — you live alone.",
    )
