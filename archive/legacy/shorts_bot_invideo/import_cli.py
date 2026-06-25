"""Register exported MP4 from InVideo into draft pack."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from rich.console import Console

from shorts_bot.invideo.script_pack import draft_pack_dir

console = Console()


def import_mp4(draft_id: int, source: Path) -> Path:
    source = source.expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Not a file: {source}")
    if source.suffix.lower() != ".mp4":
        raise ValueError("Expected .mp4 file")

    pack = draft_pack_dir(draft_id)
    pack.mkdir(parents=True, exist_ok=True)
    dest = pack / "final_short.mp4"
    if source.resolve() == dest.resolve():
        return dest
    shutil.copy2(source, dest)
    return dest


def main() -> None:
    parser = argparse.ArgumentParser(description="Copy InVideo export into draft pack")
    parser.add_argument("--draft-id", type=int, required=True)
    parser.add_argument("mp4", type=Path, help="Path to exported MP4")
    args = parser.parse_args()

    dest = import_mp4(args.draft_id, args.mp4)
    console.print(f"[green]Saved:[/green] {dest}")
    console.print(f"Upload: python3 -m shorts_bot.production.upload_canonical_cli --draft-id {args.draft_id} --video {dest}")


if __name__ == "__main__":
    main()
