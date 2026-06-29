"""One-phone hub setup tests."""

from __future__ import annotations

import json
from unittest import mock

import pytest

from shorts_bot.phone_hub.coords import get_coord
from shorts_bot.phone_hub.setup import bind_serial_to_slot, init_ui_coords, pick_adb_serial


def test_get_coord_slot_inherits_default_keys(tmp_path, monkeypatch):
    coords_file = tmp_path / "ui_coords.json"
    coords_file.write_text(
        json.dumps(
            {
                "_default": {"nav_inbox": {"x": 100, "y": 200}},
                "phone_1": {"post_button": {"x": 900, "y": 50}},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr("shorts_bot.phone_hub.coords.coords_path", lambda: coords_file)
    assert get_coord("phone_1", "nav_inbox") == (100, 200)
    assert get_coord("phone_1", "post_button") == (900, 50)


def test_init_ui_coords_from_example(tmp_path, monkeypatch):
    hub = tmp_path / "phone_hub"
    hub.mkdir()
    example = hub / "ui_coords.json.example"
    example.write_text('{"_default": {"nav_inbox": {"x": 1, "y": 2}}}', encoding="utf-8")
    dest = hub / "ui_coords.json"

    monkeypatch.setattr("shorts_bot.phone_hub.setup.settings.data_dir", tmp_path)
    monkeypatch.setattr("shorts_bot.phone_hub.setup.coords_example_path", lambda: example)

    path = init_ui_coords()
    assert path == dest
    assert dest.is_file()


def test_pick_adb_serial_auto_single():
    with mock.patch(
        "shorts_bot.phone_hub.setup.list_devices",
        return_value=[("ABC123", "device")],
    ):
        serial, auto = pick_adb_serial("auto")
        assert serial == "ABC123"
        assert auto is True


def test_pick_adb_serial_ambiguous_raises():
    with mock.patch(
        "shorts_bot.phone_hub.setup.list_devices",
        return_value=[("A", "device"), ("B", "device")],
    ):
        with pytest.raises(RuntimeError, match="2 phones"):
            pick_adb_serial("auto")


def test_bind_serial_to_slot(tmp_path, monkeypatch):
    devices_file = tmp_path / "phone_hub" / "devices.json"
    devices_file.parent.mkdir(parents=True)
    devices_file.write_text(
        json.dumps(
            {
                "slots": [
                    {
                        "slot": "phone_1",
                        "account_id": "bubble_gspgsgsorip1",
                        "adb_serial": "",
                        "label": "test",
                        "enabled": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr("shorts_bot.phone_hub.devices.devices_config_path", lambda: devices_file)
    bind_serial_to_slot("phone_1", "XYZ999")
    data = json.loads(devices_file.read_text())
    assert data["slots"][0]["adb_serial"] == "XYZ999"


def test_tick_filters_by_slot(tmp_path, monkeypatch):
    jobs_file = tmp_path / "pending_jobs.jsonl"
    monkeypatch.setattr("shorts_bot.phone_hub.jobs.jobs_path", lambda: jobs_file)

    from shorts_bot.phone_hub.jobs import enqueue_job
    from shorts_bot.phone_hub.worker import tick

    enqueue_job(
        account_id="bubble_gspgsgsorip1",
        phone_hub_slot="phone_2",
        zernio_post_id="a",
    )
    enqueue_job(
        account_id="bubble_isaac",
        phone_hub_slot="phone_1",
        zernio_post_id="b",
    )

    result = tick(dry_run=True, slot="phone_1")
    assert result.action == "dry_run_complete"
    assert result.job_id  # phone_1 job processed first matching slot filter
