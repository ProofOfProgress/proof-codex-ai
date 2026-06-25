from shorts_bot.invideo.credit_guard import assert_credit_budget, parse_credit_cost


def test_parse_credit_cost():
    assert parse_credit_cost("Generate · 4 credits") == 4
    assert parse_credit_cost("8 credits · Generate") == 8


def test_assert_credit_budget_ok():
    assert assert_credit_budget("Generate · 6 credits", max_credits=10) == 6


def test_assert_credit_budget_blocks():
    import pytest

    with pytest.raises(RuntimeError, match="40 credits"):
        assert_credit_budget("Generate · 40 credits", max_credits=10)
