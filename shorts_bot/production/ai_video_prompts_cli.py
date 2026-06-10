"""CLI — preview AI video prompts for a topic or draft segments."""

from __future__ import annotations

import argparse
import json
import sys

from rich.console import Console
from rich.panel import Panel

from shorts_bot.production.ai_video_prompts import (
    build_video_prompt_briefs,
    match_template,
    negative_block,
    segment_to_video_prompt,
    templates,
    visual_dna,
)
from shorts_bot.production.turboscribe_parser import TranscriptSegment

console = Console()


def _demo_segments(topic: str) -> list[TranscriptSegment]:
    """Typical 26s Short beat structure when no script provided."""
    return [
        TranscriptSegment(0.0, f"You're on the couch. {topic}.", "00.00"),
        TranscriptSegment(3.0, "Your thumb hovers. You don't have to open it yet.", "00.03"),
        TranscriptSegment(8.0, "Set a five-minute timer instead of scrolling.", "00.08"),
        TranscriptSegment(14.0, "Three slow breaths. Shoulders down.", "00.14"),
        TranscriptSegment(20.0, "You're still here. That counts.", "00.20"),
    ]


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Generate Soft Continuity AI video prompts (I2V/T2V clip chain)."
    )
    parser.add_argument(
        "topic",
        nargs="?",
        default="the minute before you check your phone from the couch on Sunday",
        help="Short topic or hook line",
    )
    parser.add_argument(
        "--list-templates",
        action="store_true",
        help="List all 10 production templates",
    )
    parser.add_argument(
        "--dna",
        action="store_true",
        help="Print VISUAL DNA block only",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output briefs as JSON (for pipeline integration)",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=26.0,
        help="Total audio duration for segment timing (default 26s demo)",
    )
    args = parser.parse_args(argv)

    if args.dna:
        console.print(Panel(visual_dna(), title="VISUAL DNA"))
        console.print(f"\n[dim]Negative:[/dim] {negative_block()}")
        return

    if args.list_templates:
        for t in templates():
            console.print(
                f"[bold]{t.id}[/bold] — {t.name} ({t.role}, {t.duration_seconds}s, {t.model_hint})"
            )
            console.print(f"  keywords: {', '.join(t.keywords) or '—'}")
        return

    topic = args.topic.strip()
    tmpl = match_template(topic=topic)
    console.print(f"[cyan]Matched template:[/cyan] {tmpl.id} — {tmpl.name}")
    console.print(f"[dim]Model hint:[/dim] {tmpl.model_hint} | [dim]Role:[/dim] {tmpl.role}")

    segments = _demo_segments(topic)
    briefs = build_video_prompt_briefs(segments, topic=topic, total_duration=args.duration)

    if args.json:
        payload = [
            {
                "start_seconds": b.start_seconds,
                "end_seconds": b.end_seconds,
                "filename_stem": b.filename_stem,
                "spoken_text": b.spoken_text,
                "template_id": b.template_id,
                "model_hint": b.model_hint,
                "duration_seconds": b.duration_seconds,
                "end_state": b.end_state,
                "prompt": b.prompt,
                "negative_prompt": b.negative_prompt,
            }
            for b in briefs
        ]
        json.dump(payload, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return

    for i, brief in enumerate(briefs):
        console.print()
        console.print(
            Panel(
                brief.prompt,
                title=f"Clip {i + 1} — {brief.filename_stem} ({brief.template_id}, {brief.model_hint})",
                subtitle=f"{brief.start_seconds:.1f}s–{brief.end_seconds:.1f}s | END: {brief.end_state[:60]}…",
            )
        )
        console.print(f"[dim]Negative:[/dim] {brief.negative_prompt}")

    # Single-segment preview for hook
    hook = segment_to_video_prompt(segments[0], topic=topic, template=tmpl, clip_index=0)
    console.print()
    console.print(Panel(hook, title="Hook-only prompt (clip 1, no continuity)"))


if __name__ == "__main__":
    main()
