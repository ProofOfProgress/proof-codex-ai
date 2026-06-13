"""Where to get SCP-096 (Shy Guy) mesh + auto-download for Blender renders."""

from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path

from rich.console import Console

from shorts_bot.production.blender.creature_paths import SCP096_DIR, creature_model_status
from shorts_bot.production.blender.download_creature import ensure_scp096_model

console = Console()

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
    parser = argparse.ArgumentParser(description="SCP-096 creature model — auto-download + install")
    parser.add_argument("--status", action="store_true", help="Show whether model file exists")
    parser.add_argument("--download", action="store_true", help="Download SCP-096 from GitHub (default action)")
    parser.add_argument("--force", action="store_true", help="Re-download and re-convert")
    parser.add_argument("--from-zip", type=Path, help="Unpack manual zip into creature folder")
    args = parser.parse_args()

    if args.from_zip:
        hit = install_from_zip(args.from_zip)
        console.print(f"[green]Installed → {hit}[/green]" if hit else "[yellow]Zip extracted — rename mesh to scp_096.fbx[/yellow]")
        return

    if args.status:
        console.print(json.dumps(creature_model_status(), indent=2))
        return

    # Default: auto-download (no owner file handoff)
    if not args.status and not args.from_zip:
        path = ensure_scp096_model(force=args.force)
        console.print(f"[green]Ready:[/green] {path}")


if __name__ == "__main__":
    main()
