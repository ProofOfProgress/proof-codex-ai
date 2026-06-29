"""Phone screen capture tests."""

from __future__ import annotations

import json
from pathlib import Path
from unittest import mock

from shorts_bot.phone_hub.screen import PhoneScreenReport, serial_for_slot, ui_visible_text


def test_serial_for_slot(tmp_path, monkeypatch):
    devices = tmp_path / "phone_hub" / "devices.json"
    devices.parent.mkdir(parents=True)
    devices.write_text(
        json.dumps(
            {
                "slots": [
                    {"slot": "phone_1", "adb_serial": "ABC123", "account_id": "x"},
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr("shorts_bot.phone_hub.screen._devices_path", lambda: devices)
    assert serial_for_slot("phone_1") == "ABC123"


def test_ui_visible_text_parses_xml():
    xml = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<hierarchy>
  <node text="Inbox" bounds="[0,0][100,100]" />
  <node content-desc="Drafts" bounds="[0,100][100,200]" />
</hierarchy>"""
    with mock.patch("shorts_bot.phone_hub.screen.run_adb") as run:
        run.return_value = mock.Mock(stdout=xml, ok=True)
        with mock.patch("shorts_bot.phone_hub.screen._adb_text", return_value=xml):
            lines = ui_visible_text(serial="ABC")
    assert "Inbox" in lines
    assert "Drafts" in lines


def test_report_markdown_includes_ui_lines():
    report = PhoneScreenReport(
        slot="phone_1",
        serial="ABC",
        screenshot_path=Path("/tmp/x.png"),
        ui_lines=["Inbox", "Profile"],
        gemini_summary="TikTok home screen",
    )
    md = report.to_markdown()
    assert "phone_1" in md
    assert "Inbox" in md
    assert "TikTok home screen" in md
