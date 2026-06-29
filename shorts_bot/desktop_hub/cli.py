"""CLI for desktop hub — keyboard, mouse, screenshot on owner Windows PC."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rich.console import Console

from shorts_bot.desktop_hub.client import DesktopHubClient, DesktopHubError
from shorts_bot.desktop_hub.host import default_helper_host, default_helper_port, helper_base_url


def main(argv: list[str] | None = None) -> int:
    console = Console()
    parser = argparse.ArgumentParser(
        description="Desktop hub — keyboard/mouse on owner Windows PC via local helper"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("ping", help="Check helper is reachable")
    sub.add_parser("status", help="Show helper URL + token configured")

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
    client = DesktopHubClient()

    try:
        if args.cmd == "status":
            console.print(f"helper_url: {helper_base_url()}")
            console.print(f"helper_host: {default_helper_host()}")
            console.print(f"helper_port: {default_helper_port()}")
            import os

            console.print(f"token_configured: {bool(os.environ.get('DESKTOP_HELPER_TOKEN'))}")
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
