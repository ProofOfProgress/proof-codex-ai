from shorts_bot.invideo.shop_brief import shop_brief
from shorts_bot.invideo.prompts import DEFAULT_SHOP_BRIEF, shorts_product_brief


def test_shorts_brief_includes_vertical_rules():
    brief = shorts_product_brief(
        product="Jar Grip Opener",
        hook="Jar lid won't budge? This grip tool pops it open in three seconds.",
        weakness_hint="Stuck lids ruin cooking flow.",
        strength_hint="Rubber grip pops lid with leverage.",
    )
    assert "9:16" in brief
    assert "Jar Grip Opener" in brief
    assert "PROBLEM" in brief or "problem" in brief.lower()


def test_default_shop_brief():
    assert "Car Seat Gap Filler" in DEFAULT_SHOP_BRIEF
    assert "orange cart" in DEFAULT_SHOP_BRIEF.lower() or "shopping bag" in DEFAULT_SHOP_BRIEF.lower()


def test_shop_brief_format():
    brief = shop_brief(
        product="Mini Car Vacuum",
        hook="Crushed chips in the car seat? This mini vacuum pulls it out in seconds.",
        weakness_hint="Crumb mess in seats",
        strength_hint="Handheld suction reaches cracks",
        verdict_hint="Tap the shopping bag.",
    )
    assert "SHOP CTA" in brief or "cart" in brief.lower()
    assert "NO AI Twin" in brief
    assert "Ms. Byte" in brief  # negation — do not use
