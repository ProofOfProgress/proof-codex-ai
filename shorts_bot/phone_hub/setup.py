"""One-phone hub setup — bind ADB serial, init coords, smoke-test worker."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.phone_hub.adb import list_devices
from shorts_bot.phone_hub.devices import PhoneSlot, load_phone_slots, save_phone_slots
from shorts_bot.phone_hub.jobs import enqueue_job


@dataclass
class SetupPhoneResult:
    slot: str
    serial: str
    account_id: str
    coords_path: Path
    devices_path: Path
    auto_bound: bool
    message: str


def coords_example_path() -> Path:
    return settings.data_dir / "phone_hub" / "ui_coords.json.example"


def init_ui_coords(*, force: bool = False) -> Path:
    """Copy ui_coords.json.example → ui_coords.json if missing."""
    dest = settings.data_dir / "phone_hub" / "ui_coords.json"
    src = coords_example_path()
    if dest.is_file() and not force:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    if src.is_file():
        shutil.copyfile(src, dest)
    else:
        dest.write_text(
            json.dumps(
                {
                    "_default": {
                        "nav_inbox": {"x": 950, "y": 1850},
                        "draft_row": {"x": 540, "y": 400},
                        "post_button": {"x": 900, "y": 100},
                    }
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    return dest


def pick_adb_serial(explicit: str = "") -> tuple[str, bool]:
    """
    Return (serial, auto_bound).
    Raises RuntimeError when ambiguous or none connected.
    """
    wanted = (explicit or "").strip()
    if wanted and wanted.upper() not in {"AUTO", "auto"}:
        return wanted, False

    devices = [(s, st) for s, st in list_devices() if st == "device"]
    if not devices:
        raise RuntimeError(
            "No phone connected — plug in USB, enable USB debugging, unlock screen"
        )
    if len(devices) == 1:
        return devices[0][0], True
    serials = ", ".join(s for s, _ in devices)
    raise RuntimeError(
        f"{len(devices)} phones connected — pass --serial explicitly. Found: {serials}"
    )


def bind_serial_to_slot(slot: str, serial: str) -> Path:
    """Write adb_serial for one slot; preserve other slots."""
    slot = (slot or "").strip()
    serial = (serial or "").strip()
    if not slot:
        raise RuntimeError("slot is required (e.g. phone_1)")
    if not serial:
        raise RuntimeError("serial is required")

    slots = load_phone_slots()
    if not any(s.slot == slot for s in slots):
        raise RuntimeError(f"Unknown slot {slot!r} — check accounts.json phone_hub_slot")

    updated: list[PhoneSlot] = []
    found = False
    for row in slots:
        if row.slot == slot:
            updated.append(
                PhoneSlot(
                    slot=row.slot,
                    account_id=row.account_id,
                    adb_serial=serial,
                    label=row.label,
                    enabled=row.enabled,
                )
            )
            found = True
        else:
            updated.append(row)
    if not found:
        raise RuntimeError(f"Slot {slot!r} not in phone hub map")
    return save_phone_slots(updated)


def setup_one_phone(
    slot: str,
    *,
    serial: str = "",
    init_coords: bool = True,
) -> SetupPhoneResult:
    """Bind one phone + ensure ui_coords.json exists."""
    bound_serial, auto = pick_adb_serial(serial)
    coords = init_ui_coords() if init_coords else settings.data_dir / "phone_hub" / "ui_coords.json"
    devices_path = bind_serial_to_slot(slot, bound_serial)

    account_id = next((s.account_id for s in load_phone_slots() if s.slot == slot), "")
    how = "auto-detected" if auto else "manual"
    return SetupPhoneResult(
        slot=slot,
        serial=bound_serial,
        account_id=account_id,
        coords_path=coords,
        devices_path=devices_path,
        auto_bound=auto,
        message=f"Bound {slot} → {bound_serial} ({how})",
    )


def enqueue_test_job(
    slot: str,
    *,
    job_type: str = "bubble",
    product_name: str = "test product",
) -> object:
    """Queue a harmless test job for worker dry-run / live smoke test."""
    slot = (slot or "").strip()
    account_id = next((s.account_id for s in load_phone_slots() if s.slot == slot), "")
    if not account_id:
        raise RuntimeError(f"No account mapped to {slot}")

    return enqueue_job(
        account_id=account_id,
        phone_hub_slot=slot,
        zernio_post_id="test-smoke-job",
        job_type=job_type,
        product_name=product_name,
        detail=f"smoke test ({job_type}) — safe to dry-run",
    )


def one_phone_readiness(slot: str) -> dict[str, bool | str]:
    """Checklist for owner — what's ready vs missing."""
    from shorts_bot.phone_hub.adb import device_ready
    from shorts_bot.phone_hub.coords import coords_path

    serial = next((s.adb_serial for s in load_phone_slots() if s.slot == slot), "")
    return {
        "slot": slot,
        "serial_set": bool(serial),
        "serial_connected": bool(serial and device_ready(serial)),
        "ui_coords_exists": coords_path().is_file(),
        "account_id": next((s.account_id for s in load_phone_slots() if s.slot == slot), ""),
    }
