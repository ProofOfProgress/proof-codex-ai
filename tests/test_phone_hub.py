"""Phone hub module tests (no physical phones required)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest import mock

import pytest

from shorts_bot.phone_hub.adb import AdbResult, list_devices, run_adb
from shorts_bot.phone_hub.devices import PhoneSlot, load_phone_slots, slot_for_account
from shorts_bot.phone_hub.jobs import enqueue_job, list_jobs, update_job
from shorts_bot.phone_hub.worker import run_job, tick
from shorts_bot.tiktok_shop.accounts import ShopAccount, account_by_slot, bubble_accounts
from shorts_bot.tiktok_shop.bubble_wrap_post import bubble_carousel_defaults


def test_bubble_carousel_defaults_inbox_draft():
    acct = ShopAccount(
        id="bubble_test",
        label="test",
        track="bubble_safe",
        phone_hub_slot="phone_1",
    )
    defaults = bubble_carousel_defaults(acct)
    assert defaults == {"draft": True, "publish_now": False, "auto_add_music": False}


def test_bubble_accounts_from_config():
    accts = bubble_accounts()
    assert len(accts) >= 4
    slots = {a.phone_hub_slot for a in accts}
    assert "phone_1" in slots and "phone_4" in slots


def test_account_by_slot():
    acct = account_by_slot("phone_2")
    assert acct is not None
    assert acct.id == "bubble_proofofprogresss"


def test_load_phone_slots(tmp_path, monkeypatch):
    devices_file = tmp_path / "phone_hub" / "devices.json"
    devices_file.parent.mkdir(parents=True)
    devices_file.write_text(
        json.dumps(
            {
                "slots": [
                    {
                        "slot": "phone_1",
                        "account_id": "bubble_gspgsgsorip1",
                        "adb_serial": "ABC123",
                        "label": "test",
                        "enabled": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    def fake_config_path():
        return devices_file

    monkeypatch.setattr("shorts_bot.phone_hub.devices.devices_config_path", fake_config_path)
    slots = load_phone_slots()
    phone1 = next(s for s in slots if s.slot == "phone_1")
    assert phone1.adb_serial == "ABC123"
    assert slot_for_account("bubble_gspgsgsorip1") == "phone_1"


def test_enqueue_and_tick_dry_run(tmp_path, monkeypatch):
    jobs_file = tmp_path / "pending_jobs.jsonl"

    monkeypatch.setattr("shorts_bot.phone_hub.jobs.jobs_path", lambda: jobs_file)

    job = enqueue_job(
        account_id="bubble_isaac",
        phone_hub_slot="phone_4",
        zernio_post_id="post123",
        slide1="/tmp/s1.jpg",
        slide2="/tmp/s2.jpg",
    )
    assert job.status == "pending"
    assert len(list_jobs()) == 1

    result = tick(dry_run=True)
    assert result.action == "dry_run_complete"
    updated = list_jobs(status="dry_run_complete")
    assert len(updated) == 1
    assert "wake_device" in updated[0].steps_completed


def test_run_adb_mocked(monkeypatch):
    def fake_run(cmd, **kwargs):
        return mock.Mock(returncode=0, stdout="List of devices attached\n", stderr="")

    monkeypatch.setattr("shorts_bot.phone_hub.adb.shutil.which", lambda _: "/usr/bin/adb")
    monkeypatch.setattr("shorts_bot.phone_hub.adb.subprocess.run", fake_run)
    result = run_adb("devices")
    assert result.ok


def test_worker_awaiting_phone_without_serial(tmp_path, monkeypatch):
    jobs_file = tmp_path / "jobs.jsonl"
    monkeypatch.setattr("shorts_bot.phone_hub.jobs.jobs_path", lambda: jobs_file)
    monkeypatch.setattr("shorts_bot.phone_hub.worker.resolve_serial", lambda _slot: None)

    job = enqueue_job(
        account_id="bubble_isaac",
        phone_hub_slot="phone_4",
        zernio_post_id="x",
        slide1="a",
        slide2="b",
    )
    result = run_job(job, dry_run=False)
    assert result.action == "awaiting_phone"
