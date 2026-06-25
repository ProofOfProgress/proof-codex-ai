"""Start InVideo project from a prompt — InVideo writes the script."""

from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from shorts_bot.invideo.prompts import DEFAULT_CHATGPT_PLUS_BRIEF

console = Console()

DEFAULT_PROMPT = DEFAULT_CHATGPT_PLUS_BRIEF


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Send a prompt to InVideo — it writes the script and starts the project"
    )
    parser.add_argument(
        "--prompt",
        default=None,
        help="Creative brief (InVideo writes the script). Default: ChatGPT Plus test",
    )
    parser.add_argument("--topic", default="Claude Code — terminal agent honest breakdown")
    parser.add_argument("--draft-id", type=int, default=None, help="Optional — link run to draft folder")
    parser.add_argument("--open-browser", action="store_true", help="Open project in Desktop browser")
    parser.add_argument(
        "--download",
        action="store_true",
        help="After MCP start, wait for render + browser-download MP4 (needs login)",
    )
    parser.add_argument(
        "--auto-generate",
        action="store_true",
        help="With --download: click Generate in InVideo if not rendered yet",
    )
    parser.add_argument("--from-our-script", action="store_true", help="Rare: send our pre-written script instead")
    parser.add_argument("--vibe", default=None)
    parser.add_argument("--platform", default="youtube")
    args = parser.parse_args()

    console.print(
        Panel(
            "InVideo writes the script from your prompt.\n"
            "We do NOT paste a finished script unless you pass --from-our-script.",
            title="InVideo prompt mode",
        )
    )

    if args.draft_id and args.from_our_script:
        from shorts_bot.invideo.generate import generate_from_draft

        result = generate_from_draft(
            args.draft_id,
            open_browser=args.open_browser,
            vibe=args.vibe,
            platform=args.platform,
            use_prompt=False,
        )
    elif args.draft_id:
        from shorts_bot.invideo.generate import generate_from_draft

        result = generate_from_draft(
            args.draft_id,
            open_browser=args.open_browser,
            vibe=args.vibe,
            platform=args.platform,
            use_prompt=True,
        )
    else:
        from shorts_bot.invideo.generate import generate_from_prompt

        prompt = args.prompt or DEFAULT_PROMPT
        try:
            result = generate_from_prompt(
                prompt,
                topic=args.topic,
                open_browser=args.open_browser,
                vibe=args.vibe,
                platform=args.platform,
                draft_id=args.draft_id,
            )
        except Exception as exc:
            console.print(f"[red]{exc}[/red]")
            console.print("[yellow]Log in first:[/yellow] python3 -m shorts_bot.invideo.handoff_cli")
            raise SystemExit(1) from exc

    console.print(f"[green]{result.message}[/green]")
    console.print(f"\n[bold]Project URL:[/bold]\n{result.project_url}")
    if result.script_path:
        console.print(f"\nPrompt saved: {result.script_path}")

    if args.download:
        from shorts_bot.invideo.download import download_for_draft, download_from_project_url
        from shorts_bot.invideo.script_pack import draft_pack_dir

        console.print("\n[cyan]Waiting for InVideo render + browser download…[/cyan]")
        if args.draft_id is not None:
            dl = download_for_draft(
                args.draft_id,
                project_url=result.project_url,
                wait_ready_sec=900,
                auto_generate=args.auto_generate,
                open_browser=args.open_browser,
            )
        else:
            slug_dir = result.script_path.parent if result.script_path else None
            dest = (slug_dir / "final_short.mp4") if slug_dir else Path("final_short.mp4")
            dl = download_from_project_url(
                result.project_url,
                dest,
                wait_ready_sec=900,
                auto_generate=args.auto_generate,
                open_browser=args.open_browser,
            )
        if dl.ok:
            console.print(f"[green]Downloaded:[/green] {dl.dest}")
            if args.draft_id is not None:
                console.print(
                    f"Upload: python3 -m shorts_bot.production.upload_canonical_cli "
                    f"--draft-id {args.draft_id} --video {draft_pack_dir(args.draft_id) / 'final_short.mp4'}"
                )
        else:
            console.print(f"[yellow]Download not completed:[/yellow] {dl.message}")
            console.print("[dim]Log in:[/dim] python3 -m shorts_bot.invideo.handoff_cli")
            console.print(
                "[dim]Retry:[/dim] python3 -m shorts_bot.invideo.download_cli "
                f"--project-url {result.project_url}"
                + (f" --draft-id {args.draft_id}" if args.draft_id else "")
            )
    else:
        console.print(
            "\n[bold]Next:[/bold] When InVideo finishes → "
            "python3 -m shorts_bot.invideo.download_cli --draft-id N "
            "(or add --download on generate)"
        )


if __name__ == "__main__":
    main()
