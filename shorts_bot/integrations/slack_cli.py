"""CLI — test Slack webhook."""

from __future__ import annotations

import argparse
import sys

from rich.console import Console

from shorts_bot.integrations.slack import send_test_message, slack_setup_status

console = Console()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Slack webhook utilities")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="Show Slack setup status")
    sub.add_parser("test", help="Post a test message to the webhook channel")
    autonomy = sub.add_parser("autonomy", help="Post [autonomy] command to self-talk bus")
    autonomy.add_argument("command", help="Command for BotOperations.chat (e.g. status)")
    autonomy.add_argument("--note", default="", help="Optional note under the command")

    args = parser.parse_args(argv)
    if args.cmd == "status":
        st = slack_setup_status()
        console.print(st)
        return 0
    if args.cmd == "test":
        ok, msg = send_test_message()
        if ok:
            console.print(f"[green]OK[/green] {msg}")
            return 0
        console.print(f"[red]FAIL[/red] {msg}")
        return 1
    if args.cmd == "autonomy":
        from shorts_bot.integrations.slack_autonomy import post_autonomy_command

        ok, msg = post_autonomy_command(args.command, note=args.note)
        if ok:
            console.print(f"[green]OK[/green] {msg}")
            return 0
        console.print(f"[red]FAIL[/red] {msg}")
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
