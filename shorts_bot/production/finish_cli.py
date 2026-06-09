"""One-shot: voiceover + final MP4 + upload metadata for a draft."""

from __future__ import annotations

import argparse

from rich.console import Console

from shorts_bot.config import settings
from shorts_bot.memory.store import MemoryStore
from shorts_bot.production.pack import auto_produce_draft
from shorts_bot.production.render_video import render_short_video
from shorts_bot.production.script_humanize import finalize_script
from shorts_bot.production.upload_meta import build_upload_package, write_upload_files
from shorts_bot.production.voiceover import generate_voiceover

console = Console()


def finish_draft(draft_id: int) -> str:
    store = MemoryStore(settings.database_path)
    draft = store.get_draft(draft_id)

    finalized = finalize_script(draft.topic, draft.hook, draft.script, draft.help_angle)
    store.update_draft_content(
        draft_id,
        hook=finalized.hook,
        script=finalized.script,
        help_angle=finalized.help_angle,
        quality_notes=f"AI score {finalized.final_ai_score}/100 after {finalized.passes} passes",
    )
    log_path = settings.data_dir / "production" / f"draft_{draft_id}" / "ai_detect_log.txt"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(finalized.message + "\nscores: " + str(finalized.scores_log) + "\n", encoding="utf-8")

    pack = auto_produce_draft(store, draft_id, render_images=True)
    pack_dir = pack.output_dir
    draft = store.get_draft(draft_id)
    script_path = pack_dir / "VOICEOVER_SCRIPT.txt"
    script = script_path.read_text(encoding="utf-8") if script_path.exists() else draft.script

    vo = generate_voiceover(pack_dir, draft_id=draft_id, script_text=script)
    video = render_short_video(pack_dir, draft_id=draft_id)
    package = build_upload_package(draft.topic, draft.hook, draft_id=draft_id)
    write_upload_files(pack_dir, package, draft_id=draft_id)

    return (
        f"{finalized.message}\n{pack.message}\n{vo.message}\n{video.message}\n"
        f"Style: {settings.visual_style} stick figures + speech bubbles\n"
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
