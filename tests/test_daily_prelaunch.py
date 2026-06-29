"""Tests for daily pre-launch plan and prompt."""

from __future__ import annotations

import json

from shorts_bot.daily_prelaunch.plan import pick_today_products
from shorts_bot.daily_prelaunch.prompt import render_prompt


def test_pick_today_products_avoids_recent():
    all_names = ["Alpha", "Beta", "Gamma", "Delta"]
    picked = pick_today_products(all_names, target=2)
    assert len(picked) == 2
    assert picked[0] == "Alpha"


def test_render_prompt_includes_mission():
    text = render_prompt(mission_id="m123", mission_name="Test", products=["Widget A"])
    assert "m123" in text
    assert "Widget A" in text
    assert "zero strikes" in text.lower() or "Zero strikes" in text
