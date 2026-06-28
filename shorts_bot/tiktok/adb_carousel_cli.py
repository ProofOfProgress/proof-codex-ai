"""CLI — post bubble wrap carousel via Android ADB (Mackenzie deep link)."""

from __future__ import annotations

import argparse
import json
import sys

from rich.console import Console
from rich.table import Table

from shorts_bot.tiktok.adb_carousel import post_bubble_wrap_via_adb, status_dict
from shorts_bot.tiktok.sounds import MACKENZIE_SOUND_ID, MACKENZIE_SOUND_URL

console = Console()


def _cmd_status(args: argparse.Namespace) -> int:
    data = status_dict()
    if args.json:
        console.print_json(json.dumps(data))
        return 0

    table = Table(title="TikTok ADB carousel (Lead 3)")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("ADB available", str(data.get("adb_available")))
    table.add_row("Devices", ", ".join(data.get("devices") or []) or "none")
    table.add_row("Configured device", data.get("configured_device") or "auto")
    table.add_row("Mackenzie sound ID", data.get("mackenzie_sound_id", MACKENZIE_SOUND_ID))
    table.add_row("Deep link", data.get("mackenzie_uri", ""))
    table.add_row("Sound URL", MACKENZIE_SOUND_URL)
    if data.get("error"):
        table.add_row("Error", str(data["error"]))
    console.print(table)
    return 0 if data.get("adb_available") else 1


def _cmd_post(args: argparse.Namespace) -> int:
    result = post_bubble_wrap_via_adb(
        args.slide1,
        args.slide2,
        device_id=args.device,
        draft=args.draft,
        dry_run=args.dry_run,
    )
    if args.json:
        console.print_json(
            json.dumps(
                {
                    "ok": result.ok,
                    "message": result.message,
                    "device_id": result.device_id,
                    "sound_id": result.sound_id,
                    "steps": result.steps,
                }
            )
        )
    else:
        if result.ok:
            console.print(f"[green]{result.message}[/green]")
        else:
            console.print(f"[red]{result.message}[/red]")
        for step in result.steps:
            console.print(f"  • {step}")
    return 0 if result.ok else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Post 2-slide TikTok carousel with Mackenzie sound via Android ADB",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    status_p = sub.add_parser("status", help="Check adb + Mackenzie deep link")
    status_p.add_argument("--json", action="store_true")
    status_p.set_defaults(func=_cmd_status)

    post_p = sub.add_parser("post", help="Sound-first carousel post (Lead 3)")
    post_p.add_argument("--slide1", type=str, required=True, help="Hook slide PNG/JPG")
    post_p.add_argument("--slide2", type=str, required=True, help="CTA slide PNG/JPG")
    post_p.add_argument("--device", type=str, default="", help="ADB serial (or TIKTOK_ADB_DEVICE_ID)")
    post_p.add_argument("--draft", action="store_true", help="Save to drafts instead of posting")
    post_p.add_argument("--dry-run", action="store_true", help="Print plan without touching device")
    post_p.add_argument("--json", action="store_true")
    post_p.set_defaults(func=_cmd_post)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
