"""Production supervisor — health audit + locked sequential runner."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

from shorts_bot.compliance.upload_guard import check_upload_allowed
from shorts_bot.config import settings
from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.memory.store import MemoryStore
from shorts_bot.production.horror_repair import script_needs_horror_repair
from shorts_bot.production.pipeline_lock import read_lock
from shorts_bot.production.queue_cli import _pack_dir, list_approved, next_draft_id

console = Console()


def audit_health(store: MemoryStore | None = None) -> dict:
    store = store or MemoryStore(settings.database_path)
    memory = MemoryExtensions(store)
    issues: list[str] = []
    warnings: list[str] = []

    lock = read_lock()
    if lock:
        warnings.append(f"Pipeline lock active: draft #{lock.draft_id} pid {lock.pid}")

    for d in list_approved(store):
        pack = _pack_dir(d.id)
        if script_needs_horror_repair(d.script, d.hook):
            issues.append(f"Draft #{d.id} has first-person voice drift — run --repair-draft {d.id}")
        if not (pack / "final_short.mp4").exists():
            clips = len(list((pack / "clips").glob("*.mp4"))) if (pack / "clips").is_dir() else 0
            if clips and content_stamp_mismatch(pack, d.hook, d.script):
                issues.append(f"Draft #{d.id} has {clips} stale I2V clips (script changed) — repair or --no-resume")

    nid = next_draft_id(store)
    if nid:
        draft = store.get_draft(nid)
        if draft:
            report = check_upload_allowed(
                store,
                memory,
                draft_id=draft.id,
                topic=draft.topic,
                hook=draft.hook,
                script=draft.script,
                title=draft.hook,
            )
            if not report.allowed:
                warnings.append(f"Upload guard for draft #{nid}: {'; '.join(report.issues)}")

    yt = __import__("shorts_bot.youtube.google_auth", fromlist=["auth_status"]).auth_status()
    if not yt.get("token_saved"):
        issues.append("YouTube OAuth token missing")

    return {
        "ok": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "next_draft_id": nid,
        "lock": (
            {"draft_id": lock.draft_id, "pid": lock.pid, "started_at": lock.started_at}
            if lock
            else None
        ),
    }


def content_stamp_mismatch(pack: Path, hook: str, script: str) -> bool:
    from shorts_bot.production.pipeline_integrity import content_stamp_stale

    return content_stamp_stale(pack, hook=hook, script=script) and any(pack.joinpath("clips").glob("*.mp4"))


def print_health(report: dict) -> None:
    if report["ok"] and not report["warnings"]:
        console.print("[green]System health: OK[/green]")
    else:
        console.print("[yellow]System health: needs attention[/yellow]")
    if report["issues"]:
        for i in report["issues"]:
            console.print(f"  [red]✗[/red] {i}")
    if report["warnings"]:
        for w in report["warnings"]:
            console.print(f"  [yellow]![/yellow] {w}")
    if report.get("next_draft_id"):
        console.print(f"Next pipeline draft: #{report['next_draft_id']}")


def run_once(*, upload: bool = False) -> int:
    report = audit_health()
    if report["issues"]:
        print_health(report)
        console.print("[red]Fix issues before running pipeline.[/red]")
        return 1
    nid = report.get("next_draft_id")
    if nid is None:
        console.print("[green]Queue complete — all approved drafts have final_short.mp4[/green]")
        return 0
    if read_lock():
        console.print("[yellow]Pipeline already running — supervisor exiting.[/yellow]")
        return 0
    cmd = [
        sys.executable,
        "-m",
        "shorts_bot.production.finish_cli",
        "--draft-id",
        str(nid),
        "--upload" if upload else "--no-upload",
    ]
    console.print(f"[cyan]{' '.join(cmd)}[/cyan]")
    return subprocess.call(cmd)


def main() -> None:
    parser = argparse.ArgumentParser(description="Production supervisor.")
    parser.add_argument("--health", action="store_true", help="Audit system health")
    parser.add_argument("--json", action="store_true", help="JSON output (with --health)")
    parser.add_argument("--run-once", action="store_true", help="Run next draft if healthy")
    parser.add_argument("--upload", action="store_true", help="Upload after render (with --run-once)")
    args = parser.parse_args()

    if args.health:
        report = audit_health()
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print_health(report)
        raise SystemExit(0 if report["ok"] else 1)
    if args.run_once:
        raise SystemExit(run_once(upload=args.upload))
    parser.print_help()


if __name__ == "__main__":
    main()
