"""Tests for phone hub UI helpers (no device)."""

from __future__ import annotations

from shorts_bot.phone_hub.ui import find_bounds_by_text

SAMPLE_XML = """
<hierarchy>
  <node text="Inbox" bounds="[100,200][300,400]" clickable="true"/>
  <node content-desc="Profile" bounds="[10,10][50,50]"/>
</hierarchy>
"""


def test_find_bounds_by_text():
    point = find_bounds_by_text(SAMPLE_XML, "Inbox")
    assert point == (200, 300)


def test_find_bounds_partial():
    point = find_bounds_by_text(SAMPLE_XML, "box", partial=True)
    assert point == (200, 300)
