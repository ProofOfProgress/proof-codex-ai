"""Tests for AlphaBeta Blender motion chat commands."""

from __future__ import annotations

from shorts_bot.services.chat_router import parse_blender_motion_request, parse_blender_render_request


def test_parse_blender_motion_pipe():
    r = parse_blender_motion_request("blender motion 2 wave | slow creepy wave")
    assert r == {"draft_id": 2, "phase": "wave", "prompt": "slow creepy wave"}


def test_parse_blender_motion_move_draft():
    r = parse_blender_motion_request("move draft 2 lunge: explode toward camera")
    assert r["draft_id"] == 2
    assert r["phase"] == "lunge"


def test_parse_blender_render():
    r = parse_blender_render_request("blender render 2")
    assert r == {"draft_id": 2, "background": True, "force": False}


def test_parse_blender_preview():
    r = parse_blender_render_request("blender preview 2 wave")
    assert r == {"draft_id": 2, "preview": True, "phase": "wave"}


def test_parse_rerender_natural():
    r = parse_blender_render_request("re-render draft 2 in blender")
    assert r["draft_id"] == 2
    assert r["background"] is True
