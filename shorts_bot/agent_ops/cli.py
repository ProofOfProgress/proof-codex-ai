"""CLI — watch CEO ↔ subagent missions."""

from __future__ import annotations

import argparse
import json
import sys

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from shorts_bot.agent_ops.log import append_event, list_missions, mission_events, new_mission
from shorts_bot.agent_ops.mission_continue import mission_continue_hint

console = Console()


def _print_events(events: list[dict], *, follow_header: str = "") -> None:
    if follow_header:
        console.print(follow_header)
    for row in events:
        agent = row.get("agent", "?")
        event = row.get("event", "?")
        target = row.get("target", "")
        msg = row.get("message", "")
        ts = row.get("ts", "")
        suffix = f" → {target}" if target else ""
        detail = f" — {msg}" if msg else ""
        console.print(f"[dim]{ts}[/dim] [{agent}] {event}{suffix}{detail}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Agent team mission log")
    sub = parser.add_subparsers(dest="cmd", required=True)

    start = sub.add_parser("mission", help="Mission lifecycle")
    start_sub = start.add_subparsers(dest="mission_cmd", required=True)
    mission_new = start_sub.add_parser("new", help="Create a mission and print its id")
    mission_new.add_argument("--name", required=True)
    mission_new.add_argument("--owner", default="")
    mission_cont = start_sub.add_parser(
        "continue",
        help="Suggest next CEO step from mission log (self-continue Phase 2)",
    )
    mission_cont.add_argument("--mission", default="latest")
    mission_cont.add_argument("--json", action="store_true")

    log = sub.add_parser("log", help="Append one mission event")
    log.add_argument("--mission", required=True)
    log.add_argument("--agent", required=True)
    log.add_argument("--event", required=True)
    log.add_argument("--message", default="")
    log.add_argument("--target", default="")
    log.add_argument("--data", default="", help="JSON object")

    sub.add_parser("missions", help="List recent missions")

    tail = sub.add_parser("tail", help="Show events for a mission")
    tail.add_argument("--mission", default="latest")
    tail.add_argument("--json", action="store_true")

    status = sub.add_parser("status", help="Summary of latest or named mission")
    status.add_argument("--mission", default="latest")

    args = parser.parse_args(argv)

    if args.cmd == "mission" and args.mission_cmd == "new":
        mid = new_mission(args.name, owner=args.owner)
        console.print(mid)
        return

    if args.cmd == "mission" and args.mission_cmd == "continue":
        hint = mission_continue_hint(mission_id=args.mission)
        if args.json:
            print(json.dumps(hint, indent=2))
            return
        if not hint.get("ok"):
            console.print(f"[red]{hint.get('message')}[/red]", file=sys.stderr)
            raise SystemExit(1)
        console.print(
            Panel(
                f"[bold]Action:[/bold] {hint.get('action')}\n\n{hint.get('message')}",
                title=f"Mission continue — {hint.get('mission_id')}",
            )
        )
        return

    if args.cmd == "log":
        data = json.loads(args.data) if args.data else None
        append_event(
            args.mission,
            agent=args.agent,
            event=args.event,
            message=args.message,
            target=args.target,
            data=data,
        )
        return

    if args.cmd == "missions":
        rows = list_missions()
        if not rows:
            console.print("No missions yet.")
            return
        table = Table(title="Agent missions")
        table.add_column("Mission")
        table.add_column("Name")
        table.add_column("Updated")
        table.add_column("Agents")
        table.add_column("Last")
        for row in rows:
            table.add_row(
                row["mission_id"],
                row["name"][:40],
                row["updated_at"],
                ", ".join(row["agents"][:4]),
                f"{row['last_agent']}:{row['last_event']}",
            )
        console.print(table)
        return

    mission_id = args.mission
    if mission_id == "latest":
        missions = list_missions(limit=1)
        if not missions:
            console.print("No missions yet.", file=sys.stderr)
            raise SystemExit(1)
        mission_id = missions[0]["mission_id"]

    if args.cmd == "tail":
        events = mission_events(mission_id)
        if args.json:
            print(json.dumps(events, indent=2))
            return
        _print_events(events, follow_header=f"Mission [bold]{mission_id}[/bold]")
        return

    if args.cmd == "status":
        from shorts_bot.agent_ops.log import mission_summary

        summary = mission_summary(mission_id)
        if not summary:
            console.print(f"Mission not found: {mission_id}", file=sys.stderr)
            raise SystemExit(1)
        console.print(
            Panel(
                f"[bold]{summary['name']}[/bold]\n"
                f"Mission: {summary['mission_id']}\n"
                f"Agents: {', '.join(summary['agents'])}\n"
                f"Events: {len(summary['events'])}\n"
                f"Updated: {summary['updated_at']}",
                title="Agent team status",
            )
        )
        _print_events(summary["events"][-12:], follow_header="Recent activity:")


if __name__ == "__main__":
    main()
