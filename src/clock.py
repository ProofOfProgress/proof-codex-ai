"""Agent clock — canonical time for automations, logs, and owner-local context."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

DEFAULT_OWNER_TZ = "America/Los_Angeles"
DEFAULT_OPS_TZ = "UTC"
CLOCK_PATH = Path(__file__).resolve().parent.parent / "data" / "CLOCK.json"


def _fmt(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S %Z")


def _zone(name: str) -> ZoneInfo:
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError:
        return ZoneInfo(DEFAULT_OPS_TZ)


def get_clock(
    *,
    owner_tz: str | None = None,
    ops_tz: str | None = None,
) -> dict[str, str | int | float]:
    """Return structured now — UTC ops time + owner-local wall clock."""
    owner_name = (owner_tz or os.environ.get("OWNER_TIMEZONE") or DEFAULT_OWNER_TZ).strip()
    ops_name = (ops_tz or os.environ.get("OPS_TIMEZONE") or DEFAULT_OPS_TZ).strip()

    now_utc = datetime.now(timezone.utc)
    ops_local = now_utc.astimezone(_zone(ops_name))
    owner_local = now_utc.astimezone(_zone(owner_name))

    return {
        "unix": int(now_utc.timestamp()),
        "iso_utc": now_utc.isoformat(),
        "utc": _fmt(now_utc),
        "ops_tz": ops_name,
        "ops_local": _fmt(ops_local),
        "owner_tz": owner_name,
        "owner_local": _fmt(owner_local),
        "weekday_utc": now_utc.strftime("%A"),
        "weekday_owner": owner_local.strftime("%A"),
        "date_utc": now_utc.strftime("%Y-%m-%d"),
        "date_owner": owner_local.strftime("%Y-%m-%d"),
    }


def write_clock_file(path: Path | None = None) -> Path:
    """Persist latest clock snapshot for agents that read files instead of shell."""
    target = path or CLOCK_PATH
    payload = get_clock()
    payload["updated_at"] = payload["iso_utc"]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return target


def format_clock_text(data: dict | None = None) -> str:
    d = data or get_clock()
    return (
        f"UTC:         {d['utc']}\n"
        f"Ops ({d['ops_tz']}): {d['ops_local']}\n"
        f"Owner ({d['owner_tz']}): {d['owner_local']}\n"
        f"Unix:        {d['unix']}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Agent clock — check the time")
    parser.add_argument("--json", action="store_true", help="JSON output (for agents)")
    parser.add_argument("--write", action="store_true", help=f"Write snapshot to {CLOCK_PATH}")
    parser.add_argument("--owner-tz", default=None, help="Owner timezone (default America/New_York)")
    parser.add_argument("--ops-tz", default=None, help="Ops timezone (default UTC)")
    args = parser.parse_args(argv)

    data = get_clock(owner_tz=args.owner_tz, ops_tz=args.ops_tz)

    if args.write:
        path = write_clock_file()
        data["written_to"] = str(path)

    if args.json or args.write:
        print(json.dumps(data, indent=2))
    else:
        print(format_clock_text(data))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
