"""One-shot Blender Short — download creature, render clips, stitch + SFX."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rich.console import Console

from shorts_bot.config import settings
from shorts_bot.production.render_blender import render_blender_clips
from shorts_bot.production.render_video import render_short_video
from shorts_bot.production.blender.preview_export import export_preview_assets

console = Console()


def produce_blender_short(
    draft_id: int,
    *,
    pack_dir: Path | None = None,
    force_regen: bool = False,
    output_name: str = "final_short_blender.mp4",
) -> str:
    pack = pack_dir or (settings.data_dir / "production" / f"draft_{draft_id}")
    clips_dir = pack / "clips"
    pack.mkdir(parents=True, exist_ok=True)

    console.print(f"[bold cyan]Blender produce — draft #{draft_id}[/bold cyan]")
    console.print(
        f"  backend={settings.video_backend} samples={settings.blender_samples} "
        f"clips={settings.blender_clips_per_short}×{settings.blender_clip_seconds}s"
    )

    n = render_blender_clips(
        clips_dir=clips_dir,
        draft_id=draft_id,
        pack_dir=pack,
        force_regen=force_regen,
    )
    console.print(f"[green]{n} Blender clips rendered[/green]")

    manifest_path = pack / "manifest.json"
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        manifest = {"draft_id": draft_id, "segments": []}
    manifest["render_mode"] = "blender_clips"
    manifest["video_backend"] = "blender"
    manifest["clips_rendered"] = n
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    result = render_short_video(pack, draft_id=draft_id, output_name=output_name)
    watch = export_preview_assets(pack, draft_id=draft_id)
    console.print(f"[green]Preview guide: {watch}[/green]")
    final = pack / output_name
    if output_name != "final_short.mp4":
        (pack / "final_short.mp4").unlink(missing_ok=True)
        final.rename(pack / "final_short.mp4")
        result = type(result)(
            draft_id=result.draft_id,
            output_path=pack / "final_short.mp4",
            duration_seconds=result.duration_seconds,
            message=result.message.replace(output_name, "final_short.mp4"),
        )

    return (
        f"Done — {result.output_path} ({result.duration_seconds:.1f}s)\n{result.message}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Full Blender Short production")
    parser.add_argument("--draft-id", type=int, default=2)
    parser.add_argument("--force", action="store_true", help="Re-render all clips")
    parser.add_argument("--pack-dir", type=Path, default=None)
    args = parser.parse_args()
    console.print(produce_blender_short(args.draft_id, pack_dir=args.pack_dir, force_regen=args.force))


if __name__ == "__main__":
    main()
