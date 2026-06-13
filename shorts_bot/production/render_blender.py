"""Blender 3D Short renderer — 3×10s EEVEE clips, no API cost."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from rich.console import Console

from shorts_bot.config import settings

console = Console()
BLENDER_SCRIPT = Path(__file__).resolve().parent / "blender" / "build_and_render.py"


def blender_clip_paths(clips_dir: Path, count: int | None = None) -> list[Path]:
    n = count if count is not None else settings.blender_clips_per_short
    return [clips_dir / f"blender_part_{i + 1:02d}.mp4" for i in range(n)]


def _clips_complete(clips_dir: Path, count: int) -> bool:
    for path in blender_clip_paths(clips_dir, count):
        if not path.exists() or path.stat().st_size < 5000:
            return False
    return True


def render_blender_clips(
    *,
    clips_dir: Path,
    draft_id: int,
    pack_dir: Path | None = None,
    force_regen: bool = False,
) -> int:
    """Headless Blender → blender_part_01..N.mp4 in clips_dir."""
    count = settings.blender_clips_per_short
    clips_dir.mkdir(parents=True, exist_ok=True)
    root = pack_dir or clips_dir.parent

    if not force_regen and _clips_complete(clips_dir, count):
        console.print(f"[green]Blender clips cached ({count}) — skip regen[/green]")
        return count

    cmd = [
        "blender",
        "--background",
        "--python",
        str(BLENDER_SCRIPT),
        "--",
        "--draft-id",
        str(draft_id),
        "--pack-dir",
        str(root),
    ]
    console.print(
        f"[cyan]Blender 3D — draft #{draft_id}, "
        f"{count}×{settings.blender_clip_seconds}s @ {settings.blender_samples} samples…[/cyan]"
    )
    env = {
        **__import__("os").environ,
        "BLENDER_SAMPLES": str(settings.blender_samples),
        "BLENDER_CLIP_SECONDS": str(settings.blender_clip_seconds),
    }
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "")[-3000:]
        raise RuntimeError(f"Blender render failed (exit {proc.returncode}):\n{tail}")

    rendered = sum(
        1 for p in blender_clip_paths(clips_dir, count) if p.exists() and p.stat().st_size > 5000
    )
    if rendered < count:
        raise RuntimeError(f"Blender returned {rendered}/{count} clips in {clips_dir}")

    spec = {
        "backend": "blender",
        "clips": [p.name for p in blender_clip_paths(clips_dir, count)],
        "draft_id": draft_id,
        "samples": settings.blender_samples,
        "clip_seconds": settings.blender_clip_seconds,
    }
    (clips_dir / "blender_spec.json").write_text(json.dumps(spec, indent=2), encoding="utf-8")
    return rendered
