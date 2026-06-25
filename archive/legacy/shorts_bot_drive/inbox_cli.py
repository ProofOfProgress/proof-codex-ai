"""Google Drive inbox — poll folder for InVideo exports (no paste-link step)."""

from __future__ import annotations

import argparse

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def _cmd_status() -> None:
    from shorts_bot.config import settings
    from shorts_bot.drive.client import drive_configured, drive_status_message
    from shorts_bot.drive.inbox import list_inbox_files, load_state
    from shorts_bot.youtube.google_auth import auth_status

    st = auth_status()
    console.print(Panel(drive_status_message(), title="Drive inbox"))
    console.print(f"Folder ID: {settings.google_drive_folder_id or '(not set)'}")
    console.print(f"Enabled: {settings.google_drive_inbox_enabled}")
    console.print(f"Drive API ready: {st.get('drive_ready')}")
    if st.get("needs_drive_reauth"):
        console.print(
            "[yellow]Token needs re-auth for Drive — run:[/yellow] "
            "python3 -m shorts_bot.youtube.auth_cli connect"
        )
    if not drive_configured():
        return
    state = load_state()
    console.print(f"Processed files: {len(state.get('processed_file_ids') or [])}")
    try:
        pending = list_inbox_files(include_processed=False)
    except Exception as exc:
        console.print(f"[red]Could not list inbox: {exc}[/red]")
        return
    if not pending:
        console.print("[dim]No new MP4s waiting in inbox[/dim]")
        return
    table = Table(title="New MP4s in inbox")
    table.add_column("Name")
    table.add_column("Created")
    table.add_column("Size (MB)")
    for f in pending[:10]:
        size_mb = f"{f.size / 1_000_000:.1f}" if f.size else "?"
        table.add_row(f.name, f.created_time[:19] if f.created_time else "", size_mb)
    console.print(table)


def _cmd_list() -> None:
    from shorts_bot.drive.inbox import list_inbox_files

    files = list_inbox_files(include_processed=True)
    if not files:
        console.print("[dim]Inbox folder is empty[/dim]")
        return
    table = Table(title="All MP4s in inbox (newest first)")
    table.add_column("Name")
    table.add_column("File ID")
    table.add_column("Created")
    for f in files:
        table.add_row(f.name, f.file_id[:16] + "…", f.created_time[:19] if f.created_time else "")
    console.print(table)


def _cmd_pull(draft_id: int | None, upload: bool) -> None:
    from shorts_bot.drive.inbox import pull_newest

    result = pull_newest(draft_id=draft_id, upload=upload)
    if result.ok:
        console.print(f"[green]{result.message}[/green]")
    else:
        console.print(f"[yellow]{result.message}[/yellow]")
        raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Poll Google Drive inbox folder for InVideo MP4 exports"
    )
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("status", help="Show inbox config + pending files")
    sub.add_parser("list", help="List all MP4s in inbox folder")

    pull_p = sub.add_parser("pull", help="Import newest unprocessed MP4 into draft pack")
    pull_p.add_argument("--draft-id", type=int, default=None, help="Target draft (auto-guess from filename)")
    pull_p.add_argument(
        "--upload",
        action="store_true",
        help="Upload to YouTube after import",
    )

    args = parser.parse_args()
    cmd = args.cmd or "status"

    if cmd == "status":
        console.print(
            Panel(
                "Drop finished InVideo MP4s into your Drive inbox folder.\n"
                "Name them draft_6.mp4 (or 6_chatgpt.mp4) so the agent knows which draft.\n"
                "No paste-link step needed once this is set up.",
                title="Drive handoff",
            )
        )
        _cmd_status()
        return

    if cmd == "list":
        _cmd_list()
        return

    if cmd == "pull":
        _cmd_pull(getattr(args, "draft_id", None), getattr(args, "upload", False))
        return


if __name__ == "__main__":
    main()
