"""Sequential production queue — approved drafts → finish_cli (no parallel Replicate)."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

from shorts_bot.config import settings
from shorts_bot.memory.store import Draft, MemoryStore
from shorts_bot.production.research import load_research
from shorts_bot.production.upload_meta import build_upload_package, write_upload_files

console = Console()


def _pack_dir(draft_id: int) -> Path:
    return settings.data_dir / "production" / f"draft_{draft_id}"


def list_approved(store: MemoryStore) -> list[Draft]:
    return sorted(store.list_drafts(status="approved"), key=lambda d: d.id)


def _production_status(draft_id: int) -> dict[str, str | int | bool]:
    pack = _pack_dir(draft_id)
    clip_files = (
        [p for p in (pack / "clips").glob("*.mp4") if p.stat().st_size > 10_000]
        if (pack / "clips").is_dir()
        else []
    )
    final = pack / "final_short.mp4"
    state_path = pack / "pipeline_state.json"
    steps = ""
    if state_path.exists():
        import json

        data = json.loads(state_path.read_text(encoding="utf-8"))
        steps = ", ".join(f"{k}={v}" for k, v in (data.get("steps") or {}).items())
    segment_count = 0
    manifest = pack / "manifest.json"
    if manifest.exists():
        import json

        try:
            segment_count = len(json.loads(manifest.read_text(encoding="utf-8")).get("segments") or [])
        except json.JSONDecodeError:
            segment_count = 0
    target_clips = segment_count or int(getattr(settings, "ai_video_max_beats", 10))
    return {
        "pack_exists": pack.is_dir(),
        "clips": len(clip_files),
        "clip_target": target_clips,
        "has_final": final.exists() and final.stat().st_size > 50_000,
        "has_upload_meta": (pack / "UPLOAD_READY.md").exists(),
        "steps": steps or "not started",
    }


def print_queue(store: MemoryStore) -> None:
    drafts = list_approved(store)
    if not drafts:
        console.print("[yellow]No approved drafts in queue.[/yellow]")
        return
    table = Table(title="Approved production queue (sequential)")
    table.add_column("ID")
    table.add_column("Topic")
    table.add_column("I2V")
    table.add_column("Final")
    table.add_column("Upload meta")
    table.add_column("Pipeline")
    for d in drafts:
        st = _production_status(d.id)
        table.add_row(
            str(d.id),
            (d.topic or "")[:48],
            f"{st['clips']}/{st['clip_target']}",
            "✓" if st["has_final"] else "—",
            "✓" if st["has_upload_meta"] else "—",
            str(st["steps"]),
        )
    console.print(table)


def prep_upload_meta(store: MemoryStore, draft_id: int) -> Path:
    draft = store.get_draft(draft_id)
    if draft is None:
        raise SystemExit(f"Draft #{draft_id} not found")
    pack = _pack_dir(draft_id)
    pack.mkdir(parents=True, exist_ok=True)
    research = load_research(draft.topic)
    package = build_upload_package(
        draft.topic,
        draft.hook,
        draft_id=draft_id,
        research=research,
    )
    path = write_upload_files(pack, package, draft_id=draft_id)
    console.print(f"[green]Upload meta written: {path}[/green]")
    return path


def prep_all_meta(store: MemoryStore) -> None:
    for d in list_approved(store):
        prep_upload_meta(store, d.id)


def next_draft_id(store: MemoryStore) -> int | None:
    """First approved draft without a finished MP4."""
    for d in list_approved(store):
        st = _production_status(d.id)
        if not st["has_final"]:
            return d.id
    return None


def run_finish(draft_id: int, *, upload: bool, resume: bool) -> int:
    cmd = [
        sys.executable,
        "-m",
        "shorts_bot.production.finish_cli",
        "--draft-id",
        str(draft_id),
    ]
    if upload:
        cmd.append("--upload")
    else:
        cmd.append("--no-upload")
    if not resume:
        cmd.append("--no-resume")
    console.print(f"[cyan]Running: {' '.join(cmd)}[/cyan]")
    return subprocess.call(cmd)


def main() -> None:
    parser = argparse.ArgumentParser(description="Approved draft production queue.")
    parser.add_argument("--list", action="store_true", help="Show approved drafts + status")
    parser.add_argument("--next", action="store_true", help="Print next draft id needing render")
    parser.add_argument("--prep-meta", type=int, metavar="DRAFT_ID", help="Write UPLOAD_READY.md")
    parser.add_argument("--prep-all-meta", action="store_true", help="Prep upload meta for all approved")
    parser.add_argument("--run", type=int, metavar="DRAFT_ID", help="Run finish_cli for one draft")
    parser.add_argument("--run-next", action="store_true", help="Run finish_cli for next incomplete draft")
    parser.add_argument("--upload", action="store_true", help="Upload after render (with --run)")
    parser.add_argument("--no-resume", action="store_true", help="Full rebuild (with --run)")
    parser.add_argument("--health", action="store_true", help="System health audit (supervisor)")
    parser.add_argument(
        "--repair-draft",
        type=int,
        metavar="DRAFT_ID",
        help="Fix first-person drift; reset pipeline from humanize",
    )
    args = parser.parse_args()

    store = MemoryStore(settings.database_path)

    if args.health:
        from shorts_bot.production.supervisor_cli import audit_health, print_health

        print_health(audit_health(store))
        return
    if args.repair_draft is not None:
        from shorts_bot.production.horror_repair import repair_draft_horror_voice

        console.print(f"[green]{repair_draft_horror_voice(store, args.repair_draft)}[/green]")
        return
    if args.list:
        print_queue(store)
        return
    if args.next:
        nid = next_draft_id(store)
        if nid is None:
            console.print("[green]All approved drafts have final_short.mp4[/green]")
        else:
            console.print(nid)
        return
    if args.prep_meta is not None:
        prep_upload_meta(store, args.prep_meta)
        return
    if args.prep_all_meta:
        prep_all_meta(store)
        return
    if args.run is not None:
        raise SystemExit(run_finish(args.run, upload=args.upload, resume=not args.no_resume))
    if args.run_next:
        nid = next_draft_id(store)
        if nid is None:
            console.print("[green]Queue complete — nothing to run.[/green]")
            return
        raise SystemExit(run_finish(nid, upload=args.upload, resume=not args.no_resume))

    parser.print_help()


if __name__ == "__main__":
    main()
