"""CLI for phone hub — status, devices, jobs, worker tick."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

ROOT = Path(__file__).resolve().parents[2]

from shorts_bot.phone_hub.adb import AdbError, adb_version, list_devices
from shorts_bot.phone_hub.devices import load_phone_slots, save_phone_slots
from shorts_bot.phone_hub.jobs import list_jobs
from shorts_bot.phone_hub.worker import MACKENZIE_SOUND_LABEL, tick


def main(argv: list[str] | None = None) -> int:
    console = Console()
    parser = argparse.ArgumentParser(description="Phone hub — 5 Android phones via ADB (bubble + affiliate)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="ADB + slot map + pending jobs")

    sub.add_parser("devices", help="List configured phone slots")

    jobs_p = sub.add_parser("jobs", help="List hub job queue")
    jobs_p.add_argument("--status", default="", help="Filter by status")

    tick_p = sub.add_parser("tick", help="Process pending hub job(s)")
    tick_p.add_argument("--confirm", action="store_true", help="Run real ADB automation (needs phones + serials)")
    tick_p.add_argument("--max", type=int, default=1, help="Max jobs per run (default 1)")
    tick_p.add_argument("--slot", default="", help="Only process jobs for this slot (e.g. phone_1)")
    tick_p.add_argument(
        "--only-connected",
        action="store_true",
        help="Skip jobs whose phone is not plugged in (one-phone dev mode)",
    )

    setup_p = sub.add_parser(
        "setup-phone",
        help="Bind one connected phone to a slot + init ui_coords.json",
    )
    setup_p.add_argument("--slot", default="phone_1", help="Hub slot (default phone_1 bubble)")
    setup_p.add_argument("--serial", default="auto", help="ADB serial or auto when one phone plugged in")

    bind_p = sub.add_parser("bind-serial", help="Set adb_serial for a slot")
    bind_p.add_argument("--slot", required=True)
    bind_p.add_argument("--serial", default="auto")

    sub.add_parser("init-coords", help="Copy ui_coords.json.example → ui_coords.json")

    test_p = sub.add_parser("test-job", help="Enqueue smoke-test hub job for one slot")
    test_p.add_argument("--slot", default="phone_1")
    test_p.add_argument("--type", default="bubble", choices=["bubble", "affiliate"])
    test_p.add_argument("--run", action="store_true", help="Run tick after enqueue (dry-run unless --confirm)")
    test_p.add_argument("--confirm", action="store_true", help="Live ADB with test job")

    ready_p = sub.add_parser("readiness", help="One-phone checklist (serial, coords, connection)")
    ready_p.add_argument("--slot", default="phone_1")

    screen_p = sub.add_parser(
        "screen-report",
        help="Screenshot + on-screen text (+ optional Gemini describe) for cloud agent",
    )
    screen_p.add_argument("--slot", default="phone_1")
    screen_p.add_argument("--out", default="", help="PNG output path")
    screen_p.add_argument(
        "--no-describe",
        action="store_true",
        help="Skip Gemini vision (UI text dump only — no API)",
    )

    sub.add_parser("serve", help="Loop: process inbox jobs every 45s (hub daemon)")

    init_p = sub.add_parser("init-devices", help="Write devices.json from accounts.json")
    init_p.add_argument("--force", action="store_true")

    adb_p = sub.add_parser("adb-check", help="Print adb version and connected devices")

    args = parser.parse_args(argv)

    if args.cmd == "status":
        _cmd_status(console)
        return 0
    if args.cmd == "devices":
        _cmd_devices(console)
        return 0
    if args.cmd == "jobs":
        _cmd_jobs(console, status=args.status.strip() or None)
        return 0
    if args.cmd == "tick":
        dry = not args.confirm
        from shorts_bot.phone_hub.worker import run_until_idle, tick

        slot = (args.slot or "").strip() or None
        if args.max > 1:
            results = run_until_idle(
                dry_run=dry,
                max_jobs=args.max,
                slot=slot,
                only_connected=args.only_connected,
            )
            for result in results:
                console.print(f"[bold]{result.action}[/bold] job={result.job_id} {result.detail}")
            failed = any(r.action == "failed" for r in results)
            return 1 if failed else 0
        result = tick(dry_run=dry, slot=slot, only_connected=args.only_connected)
        console.print(f"[bold]{result.action}[/bold] job={result.job_id} {result.detail}")
        return 0 if result.action not in ("failed",) else 1
    if args.cmd == "setup-phone":
        from shorts_bot.phone_hub.setup import setup_one_phone

        try:
            outcome = setup_one_phone(args.slot, serial=args.serial)
        except RuntimeError as exc:
            console.print(f"[red]{exc}[/red]")
            return 1
        console.print(f"[green]{outcome.message}[/green]")
        console.print(f"  devices: {outcome.devices_path}")
        console.print(f"  coords:  {outcome.coords_path}")
        console.print(f"  account: {outcome.account_id}")
        console.print("[dim]Next: test-job --slot {slot} --run  then  tick --confirm when draft in inbox[/dim]".format(slot=args.slot))
        return 0
    if args.cmd == "bind-serial":
        from shorts_bot.phone_hub.setup import bind_serial_to_slot, pick_adb_serial

        try:
            serial, auto = pick_adb_serial(args.serial)
            path = bind_serial_to_slot(args.slot, serial)
        except RuntimeError as exc:
            console.print(f"[red]{exc}[/red]")
            return 1
        label = "auto" if auto else "manual"
        console.print(f"[green]Bound {args.slot} → {serial}[/green] ({label}) → {path}")
        return 0
    if args.cmd == "init-coords":
        from shorts_bot.phone_hub.setup import init_ui_coords

        path = init_ui_coords()
        console.print(f"[green]UI coords ready:[/green] {path}")
        return 0
    if args.cmd == "test-job":
        from shorts_bot.phone_hub.setup import enqueue_test_job
        from shorts_bot.phone_hub.worker import tick

        job = enqueue_test_job(args.slot, job_type=args.type)
        console.print(f"[green]Test job queued:[/green] {job.id} ({args.type}) → {args.slot}")
        if args.run or args.confirm:
            result = tick(dry_run=not args.confirm, slot=args.slot)
            console.print(f"[bold]{result.action}[/bold] {result.detail}")
            return 0 if result.action not in ("failed",) else 1
        return 0
    if args.cmd == "readiness":
        from shorts_bot.phone_hub.setup import one_phone_readiness

        info = one_phone_readiness(args.slot)
        for key, val in info.items():
            ok = val is True or (key == "account_id" and val)
            color = "green" if ok else "yellow"
            if key in {"serial_set", "serial_connected", "ui_coords_exists"}:
                console.print(f"  [{color}]{key}[/{color}]: {val}")
            else:
                console.print(f"  {key}: {val}")
        return 0
    if args.cmd == "screen-report":
        from pathlib import Path

        from shorts_bot.phone_hub.screen import build_screen_report

        out = Path(args.out) if args.out else None
        try:
            report = build_screen_report(
                args.slot,
                describe=not args.no_describe,
                out_path=out,
            )
        except RuntimeError as exc:
            console.print(f"[red]{exc}[/red]")
            return 1
        console.print(report.to_markdown())
        console.print(f"\n[green]Saved[/green] {report.screenshot_path}")
        if report.ui_lines:
            console.print(f"[dim]{len(report.ui_lines)} UI text lines captured[/dim]")
        return 0
    if args.cmd == "serve":
        import subprocess

        script = ROOT / "scripts" / "hub_phone_worker.sh"
        console.print(f"[green]Starting phone worker loop[/green] ({script})")
        raise SystemExit(subprocess.call(["bash", str(script)]))
    if args.cmd == "init-devices":
        path = devices_config_path_safe()
        if path.is_file() and not args.force:
            console.print(f"[yellow]{path} exists — use --force to overwrite[/yellow]")
            return 0
        slots = load_phone_slots()
        if not slots:
            from shorts_bot.tiktok_shop.accounts import load_accounts

            slots = []
            for acct in load_accounts():
                if not acct.phone_hub_slot:
                    continue
                if not (acct.track.startswith("bubble") or acct.track.startswith("affiliate")):
                    continue
                from shorts_bot.phone_hub.devices import PhoneSlot

                slots.append(
                    PhoneSlot(
                        slot=acct.phone_hub_slot,
                        account_id=acct.id,
                        label=acct.label,
                    )
                )
        out = save_phone_slots(slots)
        console.print(f"[green]Wrote {out}[/green] ({len(slots)} slots)")
        return 0
    if args.cmd == "adb-check":
        try:
            console.print(adb_version())
            for serial, state in list_devices():
                console.print(f"  {serial}\t{state}")
        except AdbError as exc:
            console.print(f"[red]{exc}[/red]")
            return 1
        return 0
    return 2


def devices_config_path_safe():
    from shorts_bot.phone_hub.devices import devices_config_path

    return devices_config_path()


def _cmd_status(console: Console) -> None:
    table = Table(title="Phone hub status")
    table.add_column("Slot")
    table.add_column("Account")
    table.add_column("ADB serial")
    table.add_column("Connected")

    adb_serials = {}
    try:
        adb_serials = dict(list_devices())
        adb_ok = adb_version()
    except AdbError as exc:
        adb_ok = f"ERROR: {exc}"

    for slot in load_phone_slots():
        connected = "yes" if slot.adb_serial and adb_serials.get(slot.adb_serial) == "device" else "—"
        table.add_row(slot.slot, slot.account_id, slot.adb_serial or "(unset)", connected)

    console.print(table)
    console.print(f"ADB: {adb_ok}")
    pending = len(list_jobs(status="pending"))
    console.print(f"Pending hub jobs: {pending}")
    console.print(f"Mackenzie sound: {MACKENZIE_SOUND_LABEL}")


def _cmd_devices(console: Console) -> None:
    console.print(json.dumps([s.__dict__ for s in load_phone_slots()], indent=2))


def _cmd_jobs(console: Console, *, status: str | None) -> None:
    jobs = list_jobs(status=status)
    if not jobs:
        console.print("[dim]No hub jobs[/dim]")
        return
    table = Table(title="Hub jobs")
    for col in ("id", "type", "status", "slot", "account_id", "zernio_post_id", "detail"):
        table.add_column(col)
    for job in jobs:
        table.add_row(
            job.id,
            job.job_type,
            job.status,
            job.phone_hub_slot,
            job.account_id,
            job.zernio_post_id[:12],
            job.detail[:40],
        )
    console.print(table)


if __name__ == "__main__":
    raise SystemExit(main())
