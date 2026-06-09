"""One-shot: voiceover + final MP4 + upload metadata for a draft."""

from __future__ import annotations

import argparse

from rich.console import Console

from shorts_bot.config import settings
from shorts_bot.memory.store import MemoryStore
from shorts_bot.production.render_video import render_short_video
from shorts_bot.production.upload_meta import build_upload_package, write_upload_files
from shorts_bot.production.voiceover import generate_voiceover

console = Console()


def finish_draft(draft_id: int) -> str:
    store = MemoryStore(settings.database_path)
    draft = store.get_draft(draft_id)
    pack_dir = settings.data_dir / "production" / f"draft_{draft_id}"
    script_path = pack_dir / "VOICEOVER_SCRIPT.txt"
    script = script_path.read_text(encoding="utf-8") if script_path.exists() else draft.script

    vo = generate_voiceover(pack_dir, draft_id=draft_id, script_text=script)
    video = render_short_video(pack_dir, draft_id=draft_id)
    package = build_upload_package(draft.topic, draft.hook, draft_id=draft_id)
    write_upload_files(pack_dir, package, draft_id=draft_id)

    return (
        f"{vo.message}\n{video.message}\n"
        f"Upload metadata: {pack_dir / 'UPLOAD_READY.md'}\n"
        f"Title: {package.title}\n"
        f"Visibility: {package.visibility} (safer first upload)"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Finish Short: TTS + MP4 + upload metadata.")
    parser.add_argument("--draft-id", type=int, required=True)
    args = parser.parse_args()
    console.print(f"[green]{finish_draft(args.draft_id)}[/green]")


if __name__ == "__main__":
    main()
