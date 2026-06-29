"""Phone hub TikTok finish automation tests (mocked ADB)."""

from __future__ import annotations

from unittest import mock

import pytest

from shorts_bot.phone_hub import tiktok_finish


@pytest.fixture
def serial():
    return "TEST_SERIAL"


@pytest.fixture
def slot():
    return "phone_1"


def test_add_mackenzie_via_sound_page(serial, slot, monkeypatch):
    calls: list[str] = []

    monkeypatch.setattr(tiktok_finish, "open_tiktok_url", lambda url, serial: calls.append("url"))
    monkeypatch.setattr(tiktok_finish, "dismiss_overlays", lambda serial: None)
    monkeypatch.setattr(
        tiktok_finish,
        "tap_any",
        lambda *labels, serial, slot="", coord_key="", partial=True: labels[0] == "Use this sound",
    )
    monkeypatch.setattr(tiktok_finish, "_pause", lambda: None)

    ok, msg = tiktok_finish.add_mackenzie_sound(serial=serial, slot=slot)
    assert ok is True
    assert "Mackenzie" in msg


def test_add_product_link_search(serial, slot, monkeypatch):
    steps: list[str] = []

    def fake_tap(*labels, serial, slot="", coord_key="", partial=True):
        steps.append(labels[0])
        return True

    monkeypatch.setattr(tiktok_finish, "tap_any", fake_tap)
    monkeypatch.setattr(tiktok_finish, "_pause", lambda: None)
    monkeypatch.setattr(tiktok_finish.phone_ui, "input_text", lambda text, serial: steps.append(f"text:{text}"))
    monkeypatch.setattr(tiktok_finish.phone_ui, "keyevent", lambda code, serial: None)
    monkeypatch.setattr(tiktok_finish.phone_ui, "tap_by_text", lambda text, serial, partial=True: True)

    ok, msg = tiktok_finish.add_product_link(serial=serial, slot=slot, product_name="Clay Stick")
    assert ok is True
    assert "Add link" in steps
    assert "Products" in steps


def test_publish_draft(serial, slot, monkeypatch):
    monkeypatch.setattr(tiktok_finish, "tap_any", lambda *labels, serial, slot="", coord_key="", partial=True: True)
    monkeypatch.setattr(tiktok_finish, "_pause", lambda: None)
    ok, msg = tiktok_finish.publish_draft(serial=serial, slot=slot)
    assert ok is True
    assert msg == "published"
