"""Start InVideo project from a prompt — InVideo writes the script."""

from __future__ import annotations

import argparse

from rich.console import Console
from rich.panel import Panel

console = Console()

DEFAULT_PROMPT = (
    "Create a 30-second YouTube Short. Topic: ChatGPT Plus honest review. "
    "Hook: is the $20/month worth it for normal people? "
    "Give a clear Pay, Skip, or Wait verdict at the end. "
    "Tone: skeptical but fair — not hype, not affiliate energy. "
    "Use talking-head presenter + ChatGPT UI screen recordings. "
    "Captions on. 9:16 vertical. YOU write the script — this is the creative brief only."
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Send a prompt to InVideo — it writes the script and starts the project"
    )
    parser.add_argument(
        "--prompt",
        default=None,
        help="Creative brief (InVideo writes the script). Default: ChatGPT Plus test",
    )
    parser.add_argument("--topic", default="ChatGPT Plus — Pay or Skip?")
    parser.add_argument("--draft-id", type=int, default=None, help="Optional — link run to draft folder")
    parser.add_argument("--open-browser", action="store_true", help="Open project in Desktop browser")
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
    console.print(
        "\n[bold]You:[/bold] Desktop tab → InVideo generates script + video → Download MP4 when ready."
    )


if __name__ == "__main__":
    main()
