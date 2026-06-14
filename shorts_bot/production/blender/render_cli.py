"""CLI — render Peripheral Short via Blender 3D."""

from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console

from shorts_bot.production.render_blender import render_blender_clips

console = Console()


def render_blender_draft(
    draft_id: int,
    *,
    preview: bool = False,
    pack_dir: Path | None = None,
    force_regen: bool = False,
) -> str:
    from shorts_bot.config import settings

    root = pack_dir or (settings.data_dir / "production" / f"draft_{draft_id}")
    if preview:
        return _run_blender_preview(draft_id, pack_dir=root)
    count = render_blender_clips(
        clips_dir=root / "clips",
        draft_id=draft_id,
        pack_dir=root,
        force_regen=force_regen,
    )
    return f"Blender clips ({count}) in {root / 'clips'}"


def _run_blender_preview(draft_id: int, *, pack_dir: Path) -> str:
    import subprocess

    from shorts_bot.config import settings

    script = Path(__file__).resolve().parent / "build_and_render.py"
    cmd = [
        "blender",
        "--background",
        "--python",
        str(script),
        "--",
        "--draft-id",
        str(draft_id),
        "--preview",
    ]
    env = {
        **__import__("os").environ,
        "BLENDER_SAMPLES": str(settings.blender_samples),
    }
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            timeout=settings.blender_timeout_sec,
        )
    except subprocess.TimeoutExpired as exc:
        raw_tail = (exc.stderr or b"") + (exc.stdout or b"")
        if isinstance(raw_tail, bytes):
            tail = raw_tail.decode("utf-8", errors="replace")[-2000:]
        else:
            tail = str(raw_tail)[-2000:]
        raise RuntimeError(
            f"Blender preview timed out after {settings.blender_timeout_sec}s"
            + (f":\n{tail}" if tail else "")
        ) from exc
    if proc.returncode != 0:
        raise RuntimeError(f"Blender preview failed:\n{(proc.stderr or proc.stdout)[-2000:]}")
    return f"Preview: {pack_dir / 'blender_preview.png'}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Blender 3D Short render")
    parser.add_argument("--draft-id", type=int, default=2)
    parser.add_argument("--preview", action="store_true", help="Single PNG still")
    parser.add_argument("--pack-dir", type=Path, default=None)
    args = parser.parse_args()
    console.print(
        render_blender_draft(args.draft_id, preview=args.preview, pack_dir=args.pack_dir)
    )


if __name__ == "__main__":
    main()
