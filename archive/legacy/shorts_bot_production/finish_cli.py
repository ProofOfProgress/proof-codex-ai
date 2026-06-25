"""One-shot: voice clone → TurboScribe sync → MP4 → upload metadata (+ optional YT upload)."""

from __future__ import annotations

import argparse

from rich.console import Console

from shorts_bot.config import settings
from shorts_bot.memory.store import MemoryStore
from shorts_bot.production.pipeline import finish_draft_pipeline

console = Console()


def finish_draft(draft_id: int, *, upload: bool | None = None, resume: bool = True) -> str:
    store = MemoryStore(settings.database_path)
    result = finish_draft_pipeline(store, draft_id, upload_youtube=upload, resume=resume)
    lines = list(result.messages)
    lines.append(f"Pack: {result.pack_dir}")
    if result.video_path:
        lines.append(f"Video: {result.video_path}")
    if result.upload_url:
        lines.append(f"Live: {result.upload_url}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Finish Short: clone voice + TurboScribe + MP4.")
    parser.add_argument("--draft-id", type=int, required=True)
    parser.add_argument("--upload", action="store_true", help="Upload to YouTube after render")
    parser.add_argument("--no-upload", action="store_true", help="Skip YouTube upload")
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Ignore pipeline checkpoints (full rebuild)",
    )
    args = parser.parse_args()
    upload: bool | None = None
    if args.upload:
        upload = True
    if args.no_upload:
        upload = False
    console.print(
        f"[green]{finish_draft(args.draft_id, upload=upload, resume=not args.no_resume)}[/green]"
    )


if __name__ == "__main__":
    main()
