"""CLI — local phone worker for Mackenzie bubble wrap carousels."""

from __future__ import annotations

import argparse
import json
import sys
import time

from rich.console import Console
from rich.panel import Panel

from shorts_bot.tiktok.adb_carousel import status_dict
from shorts_bot.tiktok.phone_queue import load_queue, pending_jobs
from shorts_bot.tiktok.phone_worker import queue_summary, run_pending_jobs

console = Console()

EMULATOR_HELP = """
Free 100% automation (no new subscriptions):

1. Install Android Studio → create a phone AVD (Pixel, API 33+).
2. Start emulator, open Play Store → install TikTok.
3. Log into your 4 accounts (same as iPhone — one-time).
4. Enable USB debugging on the emulator (usually on by default).
5. On your laptop:
   pip install uiautomator2
   python -m uiautomator2 init
   adb devices   # should show emulator-5554
6. Run this worker (daemon watches the queue):
   python3 -m shorts_bot.tiktok.phone_worker_cli run --daemon

Cloud agent enqueues jobs → git pull → worker posts with Mackenzie + account switch.

iPhone alone cannot run ADB; the emulator on your existing laptop is the free bridge.
"""


def _cmd_status(args: argparse.Namespace) -> int:
    adb = status_dict()
    summary = queue_summary()
    if args.json:
        console.print_json(json.dumps({"adb": adb, "queue": summary}))
        return 0

    console.print(Panel(EMULATOR_HELP.strip(), title="Free automation path"))
    console.print(f"ADB: {adb}")
    console.print(f"Queue: {summary}")
    pending = pending_jobs()
    if pending:
        console.print(f"[yellow]{len(pending)} job(s) waiting[/yellow]")
        for job in pending[:10]:
            console.print(f"  • {job.id} {job.account_id} → {job.switch_label}")
    return 0


def _cmd_run(args: argparse.Namespace) -> int:
    if args.daemon:
        console.print("[cyan]Phone worker daemon — polling queue…[/cyan]")
        while True:
            result = run_pending_jobs(
                device_id=args.device or None,
                dry_run=args.dry_run,
                max_jobs=args.max_jobs,
            )
            for line in result.messages:
                console.print(line)
            if result.processed:
                console.print(
                    f"Batch: {result.succeeded} ok, {result.failed} failed "
                    f"(processed {result.processed})"
                )
            time.sleep(max(5, args.poll_sec))
    else:
        result = run_pending_jobs(
            device_id=args.device or None,
            dry_run=args.dry_run,
            max_jobs=args.max_jobs,
        )
        for line in result.messages:
            console.print(line)
        console.print(
            f"Done: {result.succeeded} ok, {result.failed} failed / {result.processed}"
        )
        return 0 if result.failed == 0 else 1
    return 0


def _cmd_list(args: argparse.Namespace) -> int:
    jobs = load_queue()
    if args.json:
        console.print_json(json.dumps([j.to_dict() for j in jobs]))
        return 0
    for job in jobs:
        console.print(
            f"{job.status:8} {job.id} {job.account_id} "
            f"switch={job.switch_label} slides={job.slide1}"
        )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Local phone worker — Mackenzie carousels + account switch (free / laptop)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    status_p = sub.add_parser("status", help="ADB + queue status")
    status_p.add_argument("--json", action="store_true")
    status_p.set_defaults(func=_cmd_status)

    run_p = sub.add_parser("run", help="Process pending queue jobs")
    run_p.add_argument("--device", default="", help="ADB serial")
    run_p.add_argument("--dry-run", action="store_true")
    run_p.add_argument("--max-jobs", type=int, default=None)
    run_p.add_argument("--daemon", action="store_true", help="Poll queue forever")
    run_p.add_argument("--poll-sec", type=int, default=30)
    run_p.set_defaults(func=_cmd_run)

    list_p = sub.add_parser("list", help="List all queue jobs")
    list_p.add_argument("--json", action="store_true")
    list_p.set_defaults(func=_cmd_list)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
