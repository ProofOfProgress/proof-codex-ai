"""CLI — download finished InVideo MP4 via browser (no file upload from owner)."""

from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download MP4 from InVideo project URL using saved browser login"
    )
    parser.add_argument("--project-url", default=None, help="InVideo project URL")
    parser.add_argument("--draft-id", type=int, default=None, help="Read URL from draft pack")
    parser.add_argument(
        "--run-dir",
        type=Path,
        default=None,
        help="Folder with invideo_project.url (e.g. data/production/invideo_runs/...)",
    )
    parser.add_argument("--output", type=Path, default=None, help="Save path (default: draft pack)")
    parser.add_argument("--resolution", default="480p", choices=("480p", "720p", "1080p"))
    parser.add_argument("--wait-ready-sec", type=int, default=900, help="Max wait for render")
    parser.add_argument(
        "--auto-generate",
        action="store_true",
        help="Click Generate if project not rendered yet, then wait",
    )
    parser.add_argument("--open-browser", action="store_true", help="Visible Desktop browser")
    args = parser.parse_args()

    if not any([args.project_url, args.draft_id is not None, args.run_dir]):
        console.print("[red]Pass --project-url, --draft-id, or --run-dir[/red]")
        raise SystemExit(2)

    console.print(
        Panel(
            "Uses your InVideo login in the saved browser profile.\n"
            "No file upload from you — the agent clicks Download in InVideo.",
            title="InVideo browser download",
        )
    )

    from shorts_bot.invideo.download import (
        download_for_draft,
        download_from_project_url,
        download_latest_run,
        read_project_url,
    )
    from shorts_bot.invideo.script_pack import draft_pack_dir

    try:
        if args.draft_id is not None:
            result = download_for_draft(
                args.draft_id,
                project_url=args.project_url,
                dest_name=(args.output.name if args.output else "final_short.mp4"),
                wait_ready_sec=args.wait_ready_sec,
                auto_generate=args.auto_generate,
                resolution=args.resolution,
                open_browser=args.open_browser,
            )
        elif args.run_dir:
            dest = args.output or (args.run_dir / "final_short.mp4")
            result = download_latest_run(
                args.run_dir,
                dest_name=dest.name,
                wait_ready_sec=args.wait_ready_sec,
                auto_generate=args.auto_generate,
                resolution=args.resolution,
                open_browser=args.open_browser,
            )
            if args.output and result.ok and result.dest:
                result.dest.rename(args.output)
                result.dest = args.output
        else:
            dest = args.output or Path("final_short.mp4")
            url = read_project_url(project_url=args.project_url)
            result = download_from_project_url(
                url,
                dest,
                wait_ready_sec=args.wait_ready_sec,
                auto_generate=args.auto_generate,
                resolution=args.resolution,
                open_browser=args.open_browser,
            )
    except FileNotFoundError as exc:
        console.print(f"[red]{exc}[/red]")
        raise SystemExit(1) from exc

    if result.ok:
        console.print(f"[green]{result.message}[/green]")
        if args.draft_id is not None:
            console.print(
                f"\n[bold]Upload:[/bold]\n"
                f"python3 -m shorts_bot.production.upload_canonical_cli "
                f"--draft-id {args.draft_id} --video {draft_pack_dir(args.draft_id) / 'final_short.mp4'}"
            )
    else:
        console.print(f"[red]{result.message}[/red]")
        if result.state.value == "login":
            console.print("[yellow]Fix:[/yellow] python3 -m shorts_bot.invideo.handoff_cli")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
