"""Tests for read-only Discord ingest helpers."""

from __future__ import annotations

from shorts_bot.integrations.discord_read import parse_channel_ids, render_channel_markdown


def test_parse_channel_ids():
    assert parse_channel_ids("111, 222;333") == ["111", "222", "333"]
    assert parse_channel_ids("") == []


def test_render_channel_markdown_orders_oldest_first():
    messages = [
        {"timestamp": "2026-06-30T12:00:00Z", "author": {"username": "coach"}, "content": "newer"},
        {"timestamp": "2026-06-30T11:00:00Z", "author": {"username": "moe"}, "content": "older"},
    ]
    md = render_channel_markdown("chan1", messages)
    assert md.index("older") < md.index("newer")
