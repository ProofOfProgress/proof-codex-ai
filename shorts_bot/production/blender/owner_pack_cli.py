"""Zip 3D assets (+ optional .blend) so owner can open Peripheral scenes in Blender Desktop."""

from __future__ import annotations

import argparse
import subprocess
import zipfile
from pathlib import Path

from rich.console import Console

from shorts_bot.config import settings
from shorts_bot.production.blender.creature_paths import SCP096_DIR, resolve_creature_model
from shorts_bot.production.blender.environment_paths import DEFAULT_ENV_DIR, resolve_environment_model
from shorts_bot.production.blender.motion_exports import motion_exports_dir, resolve_motion_fbx

console = Console()
PHASES = ("open", "wave", "lunge")


def _workspace_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _save_blend(draft_id: int, pack_dir: Path) -> Path | None:
    script = Path(__file__).resolve().parent / "build_and_render.py"
    blend_path = pack_dir / f"peripheral_draft_{draft_id}.blend"
    cmd = [
        "blender",
        "--background",
        "--python",
        str(script),
        "--",
        "--draft-id",
        str(draft_id),
        "--save-blend",
        "--pack-dir",
        str(pack_dir),
    ]
    env = {**__import__("os").environ, "BLENDER_SAMPLES": str(settings.blender_samples)}
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if proc.returncode != 0:
        console.print("[yellow]Blend export failed — zip will still include FBX assets[/yellow]")
        console.print((proc.stderr or proc.stdout)[-800:])
        return None
    return blend_path if blend_path.is_file() else None


def _add_tree(zf: zipfile.ZipFile, src: Path, arc_prefix: str) -> int:
    if not src.exists():
        return 0
    count = 0
    if src.is_file():
        zf.write(src, f"{arc_prefix}/{src.name}")
        return 1
    for path in src.rglob("*"):
        if path.is_file():
            rel = path.relative_to(src)
            zf.write(path, f"{arc_prefix}/{rel.as_posix()}")
            count += 1
    return count


def build_owner_pack(
    draft_id: int,
    *,
    pack_dir: Path | None = None,
    with_blend: bool = False,
) -> Path:
    root = _workspace_root()
    pack = pack_dir or (settings.data_dir / "production" / f"draft_{draft_id}")
    pack.mkdir(parents=True, exist_ok=True)
    out = pack / f"OWNER_BLENDER_PACK_draft_{draft_id}.zip"

    blend_path: Path | None = None
    if with_blend:
        console.print("[cyan]Building .blend scene (1–2 min)…[/cyan]")
        blend_path = _save_blend(draft_id, pack)

    readme = Path(__file__).resolve().parent / "README_FOR_OWNER.md"
    how_to = pack / "HOW_TO_HELP.md"
    how_to.write_text(
        "# How to help with draft #{draft}\n\n"
        "1. Install Blender 4.x from blender.org\n"
        "2. Open `peripheral_draft_{draft}.blend` if included, OR import FBX from `assets/`\n"
        "3. Fix lighting / textures / camera\n"
        "4. Save and send the .blend back to the agent\n\n"
        "Refs: LIGHTS ARE OFF — youtube.com/shorts/R7cEIG_gqLU · youtube.com/shorts/zCA4NuvoVXI\n"
        .format(draft=draft_id),
        encoding="utf-8",
    )

    env_dir = root / DEFAULT_ENV_DIR
    creature_dir = root / SCP096_DIR
    motion_dir = motion_exports_dir()

    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        if readme.is_file():
            zf.write(readme, "README_FOR_OWNER.md")
        zf.write(how_to, "HOW_TO_HELP.md")
        if blend_path and blend_path.is_file():
            zf.write(blend_path, blend_path.name)
        _add_tree(zf, env_dir, "assets/environments/gas_station")
        _add_tree(zf, creature_dir, "assets/creatures/scp_096")
        for phase in PHASES:
            fbx = resolve_motion_fbx(draft_id, phase)
            if fbx and fbx.is_file():
                zf.write(fbx, f"assets/motion_exports/{fbx.name}")
        # Preview stills if any
        previews = pack / "preview_frames"
        if previews.is_dir():
            for png in sorted(previews.glob("*.png"))[:8]:
                zf.write(png, f"previews/{png.name}")

    how_to.unlink(missing_ok=True)
    size_mb = out.stat().st_size / (1024 * 1024)
    console.print(f"[green]Ready[/green] {out} ({size_mb:.1f} MB)")
    console.print("Download from Cursor file tree, unzip, open in Blender 4.x")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Owner zip — Blender assets + optional .blend")
    parser.add_argument("--draft-id", type=int, default=2)
    parser.add_argument("--pack-dir", type=Path, default=None)
    parser.add_argument(
        "--with-blend",
        action="store_true",
        help="Generate peripheral_draft_N.blend inside the zip (slower)",
    )
    args = parser.parse_args()

    env = resolve_environment_model()
    creature = resolve_creature_model()
    console.print("[cyan]Assets:[/cyan]")
    console.print(f"  environment: {env or 'MISSING'}")
    console.print(f"  creature:    {creature or 'MISSING'}")
    for phase in PHASES:
        fbx = resolve_motion_fbx(args.draft_id, phase)
        console.print(f"  motion {phase}: {fbx.name if fbx else 'MISSING'}")

    build_owner_pack(args.draft_id, pack_dir=args.pack_dir, with_blend=args.with_blend)


if __name__ == "__main__":
    main()
