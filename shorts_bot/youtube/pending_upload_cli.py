"""CLI — queue and process deferred YouTube uploads (YPP gap)."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(description="Pending upload queue (YPP min gap)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    enq = sub.add_parser("enqueue", help="Add draft to queue")
    enq.add_argument("--draft-id", type=int, required=True)
    enq.add_argument("--video", type=Path, required=True)
    enq.add_argument("--publish-hours", type=float, default=21.0)
    enq.add_argument("--topic", default="")

    sub.add_parser("list", help="Show queue")
    run = sub.add_parser("process", help="Upload due items")
    run.add_argument("--force", action="store_true")

    args = parser.parse_args()
    from shorts_bot.youtube.pending_uploads import (
        enqueue_upload,
        load_queue,
        process_due_uploads,
    )

    if args.cmd == "enqueue":
        publish_at = datetime.now(timezone.utc) + timedelta(hours=args.publish_hours)
        item = enqueue_upload(
            draft_id=args.draft_id,
            video_path=args.video,
            publish_at=publish_at,
            topic=args.topic,
        )
        console.print(
            f"[green]Queued draft #{args.draft_id}[/green] → publish {item.publish_at}\n"
            f"Run: python3 -m shorts_bot.youtube.pending_upload_cli process"
        )
        return

    if args.cmd == "list":
        items = load_queue()
        if not items:
            console.print("Queue empty.")
            return
        table = Table(title="Pending uploads")
        table.add_column("Draft")
        table.add_column("Publish (UTC)")
        table.add_column("Status")
        table.add_column("Video")
        for i in items:
            status = "ready" if i.video_exists() else "missing MP4 on this machine"
            table.add_row(str(i.draft_id), i.publish_at[:19], status, Path(i.video_path).name)
        console.print(table)
        return

    results = process_due_uploads(force=args.force)
    for r in results:
        if r.get("ok"):
            console.print(f"[green]Draft #{r['draft_id']}[/green] → {r.get('url')}")
        else:
            console.print(f"[yellow]Draft #{r['draft_id']}[/yellow] — {r.get('message')}")


if __name__ == "__main__":
    main()
