"""Force-regenerate specific I2V clips for a draft pack."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rich.console import Console

from shorts_bot.config import settings
from shorts_bot.production.image_prompts import ImageBrief
from shorts_bot.production.render_ai_video import render_ai_video_clip
from shorts_bot.production.turboscribe_parser import TranscriptSegment

console = Console()


def regen_clips(
    draft_id: int,
    stems: list[str],
    *,
    pack_dir: Path | None = None,
    force: bool = True,
) -> list[Path]:
    root = pack_dir or (settings.data_dir / "production" / f"draft_{draft_id}")
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    segments = manifest.get("segments") or []
    topic = str(manifest.get("topic") or "")
    images_dir = root / "images"
    clips_dir = root / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)

    stem_set = {s.strip() for s in stems if s.strip()}
    rendered: list[Path] = []

    for i, seg in enumerate(segments):
        stem = Path(seg["filename"]).stem
        if stem not in stem_set:
            continue
        clip_path = clips_dir / f"{stem}.mp4"
        image_path = images_dir / f"{stem}.png"
        if force:
            for path in (clip_path, image_path, clip_path.with_suffix(".error.txt")):
                if path.exists():
                    path.unlink()

        prompt_path = root / str(seg.get("prompt_file", f"prompts/{stem}.txt"))
        prompt = prompt_path.read_text(encoding="utf-8").strip() if prompt_path.exists() else ""
        spoken = str(seg.get("spoken_text") or "")
        brief = ImageBrief(
            start_seconds=float(seg.get("start_seconds", 0)),
            end_seconds=float(seg.get("end_seconds", 0)),
            filename_stem=stem,
            spoken_text=spoken,
            prompt=prompt,
        )
        tseg = TranscriptSegment(
            start_seconds=float(seg.get("start_seconds", 0)),
            text=spoken,
            label=stem,
        )
        console.print(f"[cyan]Regenerating I2V clip {stem}…[/cyan]")
        ok = render_ai_video_clip(
            brief,
            tseg,
            topic=topic,
            clip_index=i,
            image_path=images_dir / f"{stem}.png",
            clip_path=clip_path,
            pack_dir=root,
        )
        if ok:
            rendered.append(clip_path)
            console.print(f"[green]OK {clip_path}[/green]")
        else:
            err = clip_path.with_suffix(".error.txt")
            console.print(f"[red]Failed {stem}: {err.read_text()[:200] if err.exists() else 'unknown'}[/red]")

    return rendered


def main() -> None:
    parser = argparse.ArgumentParser(description="Regenerate selected I2V clips")
    parser.add_argument("--draft-id", type=int, required=True)
    parser.add_argument("--stems", required=True, help="Comma-separated stems e.g. 00.06,00.11")
    parser.add_argument("--pack-dir", type=Path, default=None)
    parser.add_argument("--render", action="store_true", help="Rebuild final_short.mp4 after regen")
    args = parser.parse_args()

    stems = [s.strip() for s in args.stems.split(",")]
    regen_clips(args.draft_id, stems, pack_dir=args.pack_dir, force=True)

    if args.render:
        from shorts_bot.production.render_video import render_short_video

        result = render_short_video(
            args.pack_dir or (settings.data_dir / "production" / f"draft_{args.draft_id}"),
            draft_id=args.draft_id,
        )
        console.print(f"[green]{result.message}[/green]")


if __name__ == "__main__":
    main()
