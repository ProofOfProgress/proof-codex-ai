"""Build long_compilation MP4 by stitching finished Shorts into 16:9."""

from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console

from shorts_bot.config import settings
from shorts_bot.memory.store import MemoryStore
from shorts_bot.production.long_form_render import render_compilation
from shorts_bot.production.long_upload_meta import package_from_pack_dir, write_long_upload_files
from shorts_bot.production.short_video_resolver import resolve_final_short_video
from shorts_bot.production.winner_selection import pick_compilation_drafts

console = Console()


def _next_pack_id() -> str:
    root = settings.data_dir / "production"
    existing = sorted(root.glob("long_compilation_*"))
    if not existing:
        return "long_compilation_001"
    last = existing[-1].name
    try:
        num = int(last.rsplit("_", 1)[-1])
        return f"long_compilation_{num + 1:03d}"
    except ValueError:
        return "long_compilation_001"


def build_compilation(
    *,
    draft_ids: list[int],
    pack_id: str | None = None,
    output_root: Path | None = None,
) -> Path:
    if len(draft_ids) < 2:
        raise ValueError("Need at least 2 draft IDs for a compilation")

    store = MemoryStore(settings.database_path)
    pack_id = pack_id or _next_pack_id()
    pack_dir = output_root or (settings.data_dir / "production" / pack_id)

    segments: list[tuple[int, Path, str, str]] = []
    for did in draft_ids:
        draft = store.get_draft(did)
        src_dir = settings.data_dir / "production" / f"draft_{did}"
        video = resolve_final_short_video(src_dir)
        if video is None:
            raise FileNotFoundError(f"No final_short MP4 for draft #{did}")
        segments.append((did, video, draft.topic, draft.hook))

    result = render_compilation(pack_dir=pack_dir, segments=segments)
    package = package_from_pack_dir(pack_dir)
    write_long_upload_files(pack_dir, package, pack_id=pack_id)

    console.print(f"[green]{result.message}[/green]")
    console.print(f"[dim]Pack: {pack_dir}[/dim]")
    return result.output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Stitch 2+ finished Shorts into 16:9 long_compilation (blur pillarbox)"
    )
    parser.add_argument(
        "--draft-ids",
        type=str,
        default="",
        help="Comma-separated draft IDs (e.g. 2,3,1). Omit to auto-pick winners.",
    )
    parser.add_argument("--limit", type=int, default=3, help="Auto-pick count when --draft-ids omitted")
    parser.add_argument("--pack-id", type=str, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()

    if args.draft_ids.strip():
        ids = [int(x.strip()) for x in args.draft_ids.split(",") if x.strip()]
    else:
        picks = pick_compilation_drafts(limit=args.limit)
        if len(picks) < 2:
            raise SystemExit("Need at least 2 drafts with rendered Shorts")
        ids = [p.draft_id for p in picks]
        console.print(f"[cyan]Auto-picked drafts: {ids}[/cyan]")

    build_compilation(
        draft_ids=ids,
        pack_id=args.pack_id,
        output_root=args.output_dir,
    )


if __name__ == "__main__":
    main()
