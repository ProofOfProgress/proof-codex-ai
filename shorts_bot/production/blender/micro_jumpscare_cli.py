"""Render a 3-second volume-blast jumpscare Short (Blender lunge + sting, no VO)."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from rich.console import Console

from shorts_bot.config import settings
from shorts_bot.production.blender.preview_export import export_preview_assets
from shorts_bot.production.micro_jumpscare_render import render_micro_jumpscare_final

console = Console()
BLENDER_SCRIPT = Path(__file__).resolve().parent / "build_and_render.py"


def produce_micro_jumpscare(
    draft_id: int,
    *,
    pack_dir: Path | None = None,
    force: bool = False,
    seconds: float | None = None,
    samples: int | None = None,
    extra_env: dict[str, str] | None = None,
    use_mixamo: bool | None = None,
) -> str:
    pack = pack_dir or (settings.data_dir / "production" / f"draft_{draft_id}")
    pack.mkdir(parents=True, exist_ok=True)
    clip = pack / "clips" / "blender_part_01.mp4"
    sec = seconds if seconds is not None else settings.micro_jumpscare_seconds
    smp = samples if samples is not None else max(24, settings.blender_samples)
    from shorts_bot.production.blender.motion_backend import motion_env, motion_source_label, use_downloaded_motion

    motion_label = motion_source_label(use_mixamo=use_mixamo)

    if force or not clip.is_file() or clip.stat().st_size < 5000:
        clip.unlink(missing_ok=True)
        from shorts_bot.production.blender.download_creature import ensure_scp096_model
        from shorts_bot.production.blender.download_environment import ensure_gas_station_environment

        try:
            ensure_scp096_model(force=force)
        except Exception as exc:
            console.print(f"[yellow]Creature download skipped: {exc}[/yellow]")
        try:
            ensure_gas_station_environment(force=force)
        except Exception as exc:
            console.print(f"[yellow]Environment download skipped: {exc}[/yellow]")

        cmd = [
            "blender",
            "--background",
            "--python",
            str(BLENDER_SCRIPT),
            "--",
            "--draft-id",
            str(draft_id),
            "--pack-dir",
            str(pack),
            "--micro-jumpscare",
            "--seconds",
            str(sec),
            "--samples",
            str(smp),
        ]
        console.print(
            f"[cyan]Micro jumpscare — draft #{draft_id}, {sec:.1f}s lunge @ {smp} samples…[/cyan]"
        )
        from shorts_bot.production.blender.motion_exports import list_motion_exports

        if use_downloaded_motion() or (use_mixamo is True):
            fbx_hits = list_motion_exports(draft_id)
            if fbx_hits.get("lunge"):
                console.print(f"[yellow]Mixamo lunge (opt-in)[/yellow] → {fbx_hits['lunge'].name}")
        else:
            console.print("[cyan]Procedural lunge[/cyan] — learned motion (Mixamo off)")
        env = {
            **__import__("os").environ,
            "BLENDER_INCLUDE_CREATURE": "1",
            "BLENDER_MICRO_JUMPSCARE": "1",
            "BLENDER_CREATURE_ONLY": "1",
            "BLENDER_CREATURE_TARGET_HEIGHT": str(settings.micro_jumpscare_creature_height),
            "BLENDER_MICRO_CREATURE_SCALE": str(settings.micro_jumpscare_creature_scale),
            **motion_env(use_mixamo=use_mixamo),
        }
        if extra_env:
            env.update(extra_env)
        proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
        if proc.returncode != 0:
            tail = (proc.stderr or proc.stdout or "")[-4000:]
            raise RuntimeError(f"Blender micro render failed:\n{tail}")
        if not clip.is_file() or clip.stat().st_size < 5000:
            raise RuntimeError(f"Blender finished but clip missing: {clip}")
    else:
        console.print(f"[green]Reusing clip[/green] {clip}")

    result = render_micro_jumpscare_final(
        pack, draft_id=draft_id, clip_path=clip, motion_source=motion_label
    )
    watch = export_preview_assets(pack, draft_id=draft_id)
    console.print(f"[green]{result.message}[/green]")
    console.print(f"[green]Preview guide: {watch}[/green]")
    return (
        f"{result.message}\n"
        f"Browser: http://127.0.0.1:{settings.web_port}/preview/draft/{draft_id}?file=final_short.mp4"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="3s volume-blast jumpscare Short")
    parser.add_argument("--draft-id", type=int, default=2)
    parser.add_argument("--pack-dir", type=Path, default=None)
    parser.add_argument("--force", action="store_true", help="Re-render Blender clip")
    parser.add_argument("--seconds", type=float, default=None)
    parser.add_argument("--samples", type=int, default=None)
    parser.add_argument(
        "--use-mixamo",
        action="store_true",
        help="Opt-in downloaded Mixamo FBX (default: procedural learned lunge)",
    )
    args = parser.parse_args()
    console.print(
        produce_micro_jumpscare(
            args.draft_id,
            pack_dir=args.pack_dir,
            force=args.force,
            seconds=args.seconds,
            samples=args.samples,
            use_mixamo=True if args.use_mixamo else None,
        )
    )


if __name__ == "__main__":
    main()
