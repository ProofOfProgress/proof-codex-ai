"""Preview composited screen-text overlays for a draft pack."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rich.console import Console

from shorts_bot.config import settings
from shorts_bot.production.screen_text_overlay import save_overlay_png
from shorts_bot.production.screen_text_spec import overlays_for_segments

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(description="Preview diegetic UI overlays")
    parser.add_argument("--draft-id", type=int, required=True)
    parser.add_argument("--pack-dir", type=Path, default=None)
    args = parser.parse_args()

    pack = args.pack_dir or (settings.data_dir / "production" / f"draft_{args.draft_id}")
    manifest = json.loads((pack / "manifest.json").read_text(encoding="utf-8"))
    segments = manifest.get("segments") or []
    specs = overlays_for_segments(
        segments,
        visual_beats=manifest.get("visual_beats"),
        hook=str(manifest.get("hook") or ""),
        topic=str(manifest.get("topic") or ""),
    )
    out_dir = pack / "screen_text_previews"
    out_dir.mkdir(exist_ok=True)
    for i, spec in enumerate(specs):
        if spec is None:
            continue
        path = save_overlay_png(spec, out_dir / f"segment_{i:02d}_{spec.kind}.png")
        console.print(f"[green]{path}[/green] — {spec.primary}")
    console.print(f"Saved {sum(1 for s in specs if s)} overlay preview(s) → {out_dir}")


if __name__ == "__main__":
    main()
