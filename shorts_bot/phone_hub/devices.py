"""Map phone hub slots (phone_1..phone_5) to ADB serials and TikTok accounts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.tiktok_shop.accounts import ShopAccount, load_accounts


@dataclass(frozen=True)
class PhoneSlot:
    slot: str
    account_id: str
    adb_serial: str = ""
    label: str = ""
    enabled: bool = True


def devices_config_path() -> Path:
    return settings.data_dir / "phone_hub" / "devices.json"


def load_phone_slots() -> list[PhoneSlot]:
    """Load slot map; merge accounts.json phone_hub_slot when serial file is sparse."""
    path = devices_config_path()
    file_rows: dict[str, dict] = {}
    if path.is_file():
        raw = json.loads(path.read_text(encoding="utf-8"))
        for row in raw.get("slots", []):
            if isinstance(row, dict) and row.get("slot"):
                file_rows[str(row["slot"])] = row

    slots: list[PhoneSlot] = []
    for acct in load_accounts():
        if not acct.phone_hub_slot:
            continue
        if not (acct.track.startswith("bubble") or acct.track.startswith("affiliate")):
            continue
        row = file_rows.get(acct.phone_hub_slot, {})
        slots.append(
            PhoneSlot(
                slot=acct.phone_hub_slot,
                account_id=acct.id,
                adb_serial=str(row.get("adb_serial") or "").strip(),
                label=str(row.get("label") or acct.label).strip(),
                enabled=bool(row.get("enabled", True)),
            )
        )
    slots.sort(key=lambda s: s.slot)
    return slots


def slot_for_account(account_id: str) -> str | None:
    for slot in load_phone_slots():
        if slot.account_id == account_id:
            return slot.slot
    return None


def account_for_slot(slot: str) -> ShopAccount | None:
    slot = (slot or "").strip()
    for acct in load_accounts():
        if acct.phone_hub_slot == slot and (
            acct.track.startswith("bubble") or acct.track.startswith("affiliate")
        ):
            return acct
    return None


def resolve_serial(slot: str) -> str | None:
    for row in load_phone_slots():
        if row.slot == slot and row.adb_serial:
            return row.adb_serial
    return None


def save_phone_slots(slots: list[PhoneSlot]) -> Path:
    path = devices_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "_note": "Fill adb_serial when phones arrive. One phone = one TikTok — never switch accounts.",
        "slots": [
            {
                "slot": s.slot,
                "account_id": s.account_id,
                "adb_serial": s.adb_serial,
                "label": s.label,
                "enabled": s.enabled,
            }
            for s in slots
        ],
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path
