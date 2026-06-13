"""Where to get SCP-096 (Shy Guy) mesh + how to install for Blender renders."""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from shorts_bot.production.blender.creature_paths import SCP096_DIR, creature_model_status

console = Console()

SKETCHFAB_SCP096 = "https://sketchfab.com/3d-models/scp-096-7074212c3ba54d0d959c48c55b8fefce"
MODELS_RESOURCE = "https://models.spriters-resource.com/pc_computer/scpsecretlaboratory/asset/356546/"


def print_install_guide() -> None:
    console.print(
        Panel(
            "\n".join(
                [
                    "[bold]SCP-096 → Peripheral Form 2[/bold]",
                    "",
                    "1. Download a free model (CC license — fan art, not Nintendo Shy Guy):",
                    f"   • Sketchfab: {SKETCHFAB_SCP096}",
                    f"   • Or Models Resource (FBX + textures): {MODELS_RESOURCE}",
                    "",
                    "2. Export / pick [cyan]FBX[/cyan] or [cyan]GLB[/cyan] (best for Blender).",
                    "",
                    f"3. Put files here:\n   [green]{SCP096_DIR}/[/green]",
                    "   Name mesh: scp_096.fbx (or .glb / .obj)",
                    "   Keep texture PNGs in the same folder.",
                    "",
                    "4. Preview:",
                    "   python3 -m shorts_bot.production.blender.render_cli --draft-id 2 --preview",
                    "",
                    "Pipeline auto-tweaks: darker skin, taller scale, rural Form 2 look.",
                    "Set BLENDER_CREATURE_MODEL=/path/to/file.fbx to override.",
                ]
            ),
            title="Install creature model",
        )
    )


def install_from_zip(zip_path: Path) -> Path | None:
    """Unpack zip; copy scp_096.fbx (+ textures) into channel/assets/creatures/scp_096/."""
    if not zip_path.is_file():
        raise FileNotFoundError(zip_path)
    SCP096_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(SCP096_DIR)
    from shorts_bot.production.blender.creature_paths import resolve_creature_model

    hit = resolve_creature_model(SCP096_DIR)
    return hit


def main() -> None:
    parser = argparse.ArgumentParser(description="SCP-096 creature model install helper")
    parser.add_argument("--status", action="store_true", help="Show whether model file exists")
    parser.add_argument("--from-zip", type=Path, help="Unpack Models Resource / Sketchfab zip")
    args = parser.parse_args()

    if args.from_zip:
        hit = install_from_zip(args.from_zip)
        console.print(f"[green]Installed → {hit}[/green]" if hit else "[yellow]Zip extracted — rename mesh to scp_096.fbx[/yellow]")
        return

    if args.status:
        import json

        console.print(json.dumps(creature_model_status(), indent=2))
        return

    print_install_guide()
    status = creature_model_status()
    if status["resolved"]:
        console.print(f"\n[green]Model ready:[/green] {status['resolved']}")
    else:
        console.print(f"\n[yellow]No model yet[/yellow] — drop FBX/GLB in {SCP096_DIR}")


if __name__ == "__main__":
    main()
