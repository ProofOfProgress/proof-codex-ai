"""Start InVideo project from draft script via MCP."""

from __future__ import annotations

import argparse

from rich.console import Console
from rich.panel import Panel

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate InVideo project from draft script")
    parser.add_argument("--draft-id", type=int, required=True)
    parser.add_argument("--open-browser", action="store_true", help="Open project in Desktop browser")
    parser.add_argument("--pack-only", action="store_true", help="Write script pack only — no MCP call")
    parser.add_argument("--vibe", default=None)
    parser.add_argument("--platform", default=None)
    args = parser.parse_args()

    if args.pack_only:
        from shorts_bot.invideo.script_pack import write_script_pack

        path = write_script_pack(args.draft_id)
        console.print(f"[green]Script pack:[/green] {path}")
        return

    from shorts_bot.invideo.generate import generate_from_draft

    console.print(Panel(f"Draft #{args.draft_id} → InVideo MCP", title="InVideo generate"))
    try:
        result = generate_from_draft(
            args.draft_id,
            open_browser=args.open_browser,
            vibe=args.vibe,
            platform=args.platform,
        )
    except Exception as exc:
        console.print(f"[red]{exc}[/red]")
        console.print("[yellow]Log in first:[/yellow] python3 -m shorts_bot.invideo.handoff_cli")
        raise SystemExit(1) from exc

    console.print(f"[green]{result.message}[/green]")
    console.print(f"\nProject URL:\n{result.project_url}")
    console.print(f"\nScript file: {result.script_path}")
    console.print(
        "\n[bold]You:[/bold] Desktop tab → wait for render → Download MP4 → "
        f"save as data/production/draft_{args.draft_id}/final_short.mp4"
    )


if __name__ == "__main__":
    main()
