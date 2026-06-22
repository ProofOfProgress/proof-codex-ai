"""Parse InVideo Generate button credit cost — abort if over budget."""

from __future__ import annotations

import re

DEFAULT_MAX_CREDITS = 10


def parse_credit_cost(text: str) -> int | None:
    """Extract credit number from button/page text like 'Generate · 4 credits'."""
    if not text:
        return None
    patterns = (
        r"generate[^\d]{0,40}(\d{1,3})\s*credits?",
        r"(\d{1,3})\s*credits?\s*·?\s*generate",
        r"(\d{1,3})\s*credits?",
    )
    lower = text.lower()
    for pat in patterns:
        m = re.search(pat, lower, re.I)
        if m:
            return int(m.group(1))
    return None


def assert_credit_budget(text: str, *, max_credits: int = DEFAULT_MAX_CREDITS) -> int:
    """
    Return parsed credit cost. Raise if over max or unknown (safe default: refuse).
    """
    cost = parse_credit_cost(text)
    if cost is None:
        raise RuntimeError(
            "Could not read credit cost on Generate button — refusing to click. "
            "Open InVideo manually and confirm Basic tier shows ≤10 credits."
        )
    if cost > max_credits:
        raise RuntimeError(
            f"InVideo wants {cost} credits — max allowed is {max_credits}. "
            "Switch to Basic + stock-only (no twin, no Pro) and retry."
        )
    return cost
