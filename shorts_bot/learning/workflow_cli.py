"""Inspect evolving daily workflow."""

from __future__ import annotations

import argparse
import json

from rich.console import Console
from rich.table import Table

from shorts_bot.learning.workflow import load_active_workflow
from shorts_bot.learning.workflow_evolve import workflow_status
from shorts_bot.learning.workflow_store import WorkflowRunStore
from shorts_bot.memory.store import MemoryStore
from shorts_bot.config import settings

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(description="Daily workflow evolution status")
    parser.add_argument("command", choices=["status", "history", "json"], nargs="?", default="status")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    store = MemoryStore(settings.database_path)

    if args.command == "status":
        from shorts_bot.learning.run_telemetry import telemetry_summary

        console.print(workflow_status(store))
        console.print("")
        console.print(telemetry_summary())
        return

    if args.command == "json":
        wf = load_active_workflow(store)
        console.print_json(json.dumps(wf.to_dict()))
        return

    runs = WorkflowRunStore(store).recent(limit=args.limit)
    table = Table(title="Recent workflow runs")
    table.add_column("ID")
    table.add_column("Ver")
    table.add_column("Draft")
    table.add_column("OK")
    table.add_column("Topic")
    table.add_column("Failed step")
    for r in runs:
        failed = next((s["step_id"] for s in r["steps"] if not s.get("ok")), "—")
        table.add_row(
            str(r["id"]),
            str(r["workflow_version"]),
            str(r.get("draft_id") or "—"),
            "yes" if r["ok"] else "no",
            (r["topic"] or "")[:40],
            failed,
        )
    console.print(table)


if __name__ == "__main__":
    main()
