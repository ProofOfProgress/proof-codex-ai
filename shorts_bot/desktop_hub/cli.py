"""CLI for desktop hub — keyboard, mouse, screenshot on owner Windows PC."""

from __future__ import annotations

import argparse
import os
import sys

from rich.console import Console
from rich.table import Table

from shorts_bot.desktop_hub.client import DesktopHubClient, DesktopHubError
from shorts_bot.desktop_hub.host import default_helper_host, default_helper_port, helper_base_url
from shorts_bot.desktop_hub.launcher import ensure_running, ensure_via_hub_ssh, ping_helper
from shorts_bot.desktop_hub.schedule import DailyClickSchedule, load_schedule, save_schedule


def main(argv: list[str] | None = None) -> int:
    console = Console()
    parser = argparse.ArgumentParser(
        description="Desktop hub — keyboard/mouse on owner Windows PC via local helper"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("ping", help="Check helper is reachable")
    sub.add_parser("status", help="Show helper URL + token configured")

    ensure_p = sub.add_parser("ensure", help="Start helper if not running")
    ensure_p.add_argument(
        "--via-hub",
        action="store_true",
        help="Cloud agent: SSH to owner hub and run ensure there",
    )
    ensure_p.add_argument("--no-launch", action="store_true", help="Only ping; do not start")

    sched = sub.add_parser("schedule", help="Daily click at same wall-clock time")
    sched_sub = sched.add_subparsers(dest="sched_cmd", required=True)
    sched_sub.add_parser("show", help="Show daily click schedule")

    set_p = sched_sub.add_parser("set-click", help="Configure daily click")
    set_p.add_argument("--hour", type=int, required=True)
    set_p.add_argument("--minute", type=int, default=0)
    set_p.add_argument("--x", type=int, required=True)
    set_p.add_argument("--y", type=int, required=True)
    set_p.add_argument("--timezone", default="America/Los_Angeles")
    set_p.add_argument("--button", default="left", choices=("left", "right", "middle"))
    set_p.add_argument("--label", default="")
    set_p.add_argument("--enable", action="store_true")
    set_p.add_argument("--disable", action="store_true")

    type_p = sub.add_parser("type", help="Type text via keyboard (not mouse-on-keys)")
    type_p.add_argument("text", help="Text to type")

    press_p = sub.add_parser("press", help="Press a single key (enter, tab, esc, ...)")
    press_p.add_argument("key")

    hotkey_p = sub.add_parser("hotkey", help="Press key combo (e.g. ctrl c)")
    hotkey_p.add_argument("keys", nargs="+")

    click_p = sub.add_parser("click", help="Move mouse and click")
    click_p.add_argument("x", type=int)
    click_p.add_argument("y", type=int)
    click_p.add_argument("--button", default="left", choices=("left", "right", "middle"))
    click_p.add_argument("--clicks", type=int, default=1)

    move_p = sub.add_parser("move", help="Move mouse without clicking")
    move_p.add_argument("x", type=int)
    move_p.add_argument("y", type=int)

    shot_p = sub.add_parser("screenshot", help="Capture screen PNG")
    shot_p.add_argument(
        "--out",
        default="",
        help="Output path (default: data/desktop_hub/last_screenshot.png)",
    )

    args = parser.parse_args(argv)

    if args.cmd == "ensure":
        if args.via_hub:
            code = ensure_via_hub_ssh()
            if code == 0:
                console.print("[green]Hub desktop helper ensure OK[/green]")
            else:
                console.print("[red]Hub desktop helper ensure failed[/red]")
            return code
        ok = ensure_running(launch=not args.no_launch)
        if ok:
            console.print("[green]Desktop helper running[/green]")
            return 0
        console.print("[red]Desktop helper not reachable[/red]")
        return 1

    if args.cmd == "schedule":
        if args.sched_cmd == "show":
            sched = load_schedule()
            table = Table(title="Daily click schedule")
            table.add_column("Field")
            table.add_column("Value")
            for key in ("enabled", "hour", "minute", "timezone", "x", "y", "button", "label"):
                table.add_row(key, str(getattr(sched, key)))
            console.print(table)
            console.print("[dim]Helper must be running — scheduler runs inside the daemon.[/dim]")
            return 0
        if args.sched_cmd == "set-click":
            enabled = True
            if args.disable:
                enabled = False
            elif not args.enable:
                prev = load_schedule()
                enabled = prev.enabled
            sched = DailyClickSchedule(
                enabled=enabled,
                hour=args.hour,
                minute=args.minute,
                timezone=args.timezone,
                x=args.x,
                y=args.y,
                button=args.button,
                label=args.label,
            )
            path = save_schedule(sched)
            console.print(f"[green]Saved {path}[/green]")
            if sched.enabled:
                console.print(
                    f"Daily click at {sched.hour:02d}:{sched.minute:02d} {sched.timezone} "
                    f"→ ({sched.x}, {sched.y})"
                )
            else:
                console.print("[yellow]Schedule saved but disabled — pass --enable to activate[/yellow]")
            return 0
        return 2

    client = DesktopHubClient()

    try:
        if args.cmd == "status":
            console.print(f"helper_url: {helper_base_url()}")
            console.print(f"helper_host: {default_helper_host()}")
            console.print(f"helper_port: {default_helper_port()}")
            console.print(f"token_configured: {bool(os.environ.get('DESKTOP_HELPER_TOKEN'))}")
            console.print(f"helper_ping: {'ok' if ping_helper() else 'down'}")
            return 0
        if args.cmd == "ping":
            msg = client.ping()
            console.print(f"[green]{msg}[/green]")
            return 0
        if args.cmd == "type":
            client.type_text(args.text)
            console.print("[green]typed[/green]")
            return 0
        if args.cmd == "press":
            client.press(args.key)
            console.print(f"[green]pressed {args.key}[/green]")
            return 0
        if args.cmd == "hotkey":
            client.hotkey(*args.keys)
            console.print(f"[green]hotkey {'+'.join(args.keys)}[/green]")
            return 0
        if args.cmd == "click":
            client.click(args.x, args.y, button=args.button, clicks=args.clicks)
            console.print(f"[green]click {args.x},{args.y}[/green]")
            return 0
        if args.cmd == "move":
            client.move(args.x, args.y)
            console.print(f"[green]move {args.x},{args.y}[/green]")
            return 0
        if args.cmd == "screenshot":
            from pathlib import Path

            result = client.screenshot()
            out = Path(args.out) if args.out else Path("data/desktop_hub/last_screenshot.png")
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(result.png_bytes)
            console.print(f"[green]saved {out}[/green] ({result.width}x{result.height})")
            return 0
    except DesktopHubError as exc:
        console.print(f"[red]{exc}[/red]")
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
