"""Validate production pack clips/stills before render or upload."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rich.console import Console

from shorts_bot.config import settings
from shorts_bot.production.pack_health import assess_pack_health

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check draft pack health — missing clips, stale stamp, jumpscare clip"
    )
    parser.add_argument("--draft-id", type=int, required=True)
    parser.add_argument("--pack-dir", type=Path, default=None)
    parser.add_argument(
        "--require-final",
        action="store_true",
        help="Also require final_short.mp4 (upload readiness)",
    )
    parser.add_argument(
        "--final-name",
        default="final_short.mp4",
        help="Final render filename to check with --require-final",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON summary",
    )
    args = parser.parse_args()

    pack = args.pack_dir or (settings.data_dir / "production" / f"draft_{args.draft_id}")
    report = assess_pack_health(
        pack,
        draft_id=args.draft_id,
        require_final_short=args.require_final,
        final_short_name=args.final_name,
    )

    if args.json:
        import json

        payload = {
            "draft_id": report.draft_id,
            "pack_dir": str(report.pack_dir),
            "ready_to_render": report.ready_to_render,
            "ready_to_upload": report.ready_to_upload,
            "segment_count": report.segment_count,
            "clip_count": report.clip_count,
            "still_fallback_count": report.still_fallback_count,
            "missing_segment_count": report.missing_segment_count,
            "issues": report.issues,
            "warnings": report.warnings,
            "segments": [
                {
                    "index": s.index,
                    "stem": s.stem,
                    "render_source": s.render_source,
                    "has_clip": s.has_clip,
                    "has_still": s.has_still,
                }
                for s in report.segments
            ],
        }
        console.print(json.dumps(payload, indent=2))
    else:
        for line in report.summary_lines():
            if "[issue]" in line:
                console.print(f"[red]{line}[/red]")
            elif "[warn]" in line:
                console.print(f"[yellow]{line}[/yellow]")
            elif "BLOCKED" in line:
                console.print(f"[red]{line}[/red]")
            else:
                console.print(f"[cyan]{line}[/cyan]")

    if not report.ready_to_render:
        sys.exit(1)
    if args.require_final and not report.ready_to_upload:
        sys.exit(1)


if __name__ == "__main__":
    main()
