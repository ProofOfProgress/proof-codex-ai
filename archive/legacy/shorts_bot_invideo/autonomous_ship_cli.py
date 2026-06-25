"""One-shot autonomous ship: one MCP brief → Generate (Basic, ≤10 credits) → download → upload."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from rich.console import Console

console = Console()


@dataclass
class AutonomousShipResult:
    ok: bool
    draft_id: int
    topic: str
    project_url: str
    video_path: Path | None
    upload_url: str | None
    message: str


def conversational_brief(
    *,
    product: str,
    hook: str,
    angle: str = "",
) -> str:
    """Single InVideo prompt — Ms. Byte, stock + UI, no twin, Basic tier."""
    from shorts_bot.invideo.ms_byte import ms_byte_brief

    return ms_byte_brief(product=product, hook=hook, angle=angle)


CLAUDE_CODE_BRIEF = conversational_brief(
    product="Claude Code",
    hook="Claude Code sounds amazing — but most people should not pay for this.",
    angle=(
        "STRENGTH: terminal agent edits multi-file repos, runs tests, git ops. "
        "WEAKNESS: bundled with Claude Pro; heavy use burns limits; weak value if you don't code. "
        "TRADEOFF: vs Cursor for editor-native workflows."
    ),
)


def run_autonomous_ship(
    *,
    draft_id: int,
    brief: str,
    topic: str,
    upload: bool = True,
    schedule_hours: float | None = None,
    max_credits: int = 10,
    wait_render_sec: int = 2400,
) -> AutonomousShipResult:
    from shorts_bot.config import settings
    from shorts_bot.invideo.generate import generate_from_prompt
    from shorts_bot.invideo.script_pack import draft_pack_dir
    from shorts_bot.invideo.ship_cli import ship
    from shorts_bot.production.upload_canonical_cli import upload_canonical

    pack = draft_pack_dir(draft_id)
    pack.mkdir(parents=True, exist_ok=True)
    (pack / "invideo_brief.txt").write_text(brief + "\n", encoding="utf-8")

    console.print(f"[cyan]Draft #{draft_id}[/cyan] — one MCP prompt to InVideo…")
    gen = generate_from_prompt(brief, topic=topic, draft_id=draft_id)
    console.print(f"[green]Project:[/green] {gen.project_url}")

    dest = pack / "final_short.mp4"
    ship(
        gen.project_url,
        dest,
        wait_render_sec=wait_render_sec,
        max_credits=max_credits,
    )

    upload_url = None
    if upload and dest.is_file() and dest.stat().st_size > 50_000:
        publish_at = None
        if schedule_hours and schedule_hours > 0:
            publish_at = datetime.now(timezone.utc) + timedelta(hours=schedule_hours)
        try:
            if publish_at:
                from shorts_bot.youtube.scheduled_upload import upload_scheduled_short

                upload_url = upload_scheduled_short(draft_id, dest, publish_at=publish_at)
            else:
                upload_url = upload_canonical(draft_id, dest, volume_warning=False)
        except RuntimeError as exc:
            if publish_at and ("24h" in str(exc) or "wait" in str(exc).lower()):
                from shorts_bot.youtube.pending_uploads import enqueue_upload

                enqueue_upload(
                    draft_id=draft_id,
                    video_path=dest,
                    publish_at=publish_at,
                    topic=topic,
                )
                upload_url = f"queued for {publish_at.isoformat()}"
            else:
                raise

        if upload_url and upload_url.startswith("http") and settings.post_upload_analytics_sync:
            from shorts_bot.youtube.post_upload import sync_analytics_after_upload

            sync_analytics_after_upload()

    return AutonomousShipResult(
        ok=bool(upload_url or dest.is_file()),
        draft_id=draft_id,
        topic=topic,
        project_url=gen.project_url,
        video_path=dest if dest.is_file() else None,
        upload_url=upload_url,
        message=upload_url or f"MP4 saved: {dest}",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Autonomous InVideo ship — one prompt, Basic tier, credit guard"
    )
    parser.add_argument("--draft-id", type=int, required=True)
    parser.add_argument("--topic", default="Claude Code — honest 30s review")
    parser.add_argument("--brief-file", type=Path, default=None)
    parser.add_argument("--claude-code", action="store_true", help="Use built-in Claude Code brief")
    parser.add_argument("--no-upload", action="store_true")
    parser.add_argument(
        "--schedule-hours",
        type=float,
        default=21.0,
        help="Hours from now to publish (default 21 — clears 20h upload gap)",
    )
    parser.add_argument("--max-credits", type=int, default=10)
    parser.add_argument("--wait-render-sec", type=int, default=2400)
    args = parser.parse_args()

    if args.claude_code or not args.brief_file:
        brief = CLAUDE_CODE_BRIEF
    else:
        brief = args.brief_file.read_text(encoding="utf-8")

    result = run_autonomous_ship(
        draft_id=args.draft_id,
        brief=brief,
        topic=args.topic,
        upload=not args.no_upload,
        schedule_hours=args.schedule_hours if not args.no_upload else None,
        max_credits=args.max_credits,
        wait_render_sec=args.wait_render_sec,
    )
    if result.ok:
        console.print(f"[green]{result.message}[/green]")
    else:
        console.print(f"[red]{result.message}[/red]")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
