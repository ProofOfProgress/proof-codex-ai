"""Auto-download CC0 gas-station environment (Elbolilloduro via itch.io).

Uses saved browser profile when itch requires the free purchase flow.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from rich.console import Console

from shorts_bot.production.blender.environment_paths import DEFAULT_ENV_DIR, resolve_environment_model

console = Console()

ITCH_GAME_URL = "https://elbolilloduro.itch.io/gas-station"
RAR_NAME = "Gas_station.rar"

ATTRIBUTION_TEXT = """Gas station environment (PSX low-poly)
Creator: Elbolilloduro
Source: https://elbolilloduro.itch.io/gas-station
Sketchfab: https://sketchfab.com/3d-models/gas-station-eeb913b90b4344ddbd7852f82a7ef160
License: CC0 1.0 (public domain)
https://creativecommons.org/publicdomain/zero/1.0/

Used as Peripheral Form 2 rural gas-station backdrop in Blender EEVEE renders.
"""


def _extract_rar(rar: Path, dest_dir: Path) -> None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    unrar = shutil.which("unrar") or shutil.which("unrar-free")
    if not unrar:
        raise RuntimeError("unrar missing — run: sudo apt-get install -y unrar-free")
    proc = subprocess.run(
        [unrar, "x", "-o+", str(rar), str(dest_dir)],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"unrar failed:\n{(proc.stderr or proc.stdout)[-1500:]}")
    fbx = dest_dir / "Gas_station" / "Models" / "Gas_station.fbx"
    if not fbx.is_file():
        raise RuntimeError(f"Expected FBX missing after extract: {fbx}")


def ensure_gas_station_environment(*, force: bool = False) -> Path:
    """Download + extract gas station if missing. Returns path to Gas_station.fbx."""
    existing = resolve_environment_model(DEFAULT_ENV_DIR)
    if existing and not force and existing.stat().st_size > 50_000:
        return existing

    DEFAULT_ENV_DIR.mkdir(parents=True, exist_ok=True)
    rar = DEFAULT_ENV_DIR / RAR_NAME
    fbx = DEFAULT_ENV_DIR / "Gas_station" / "Models" / "Gas_station.fbx"

    if force or not fbx.is_file() or fbx.stat().st_size < 50_000:
        if force or not rar.is_file() or rar.stat().st_size < 1_000_000:
            console.print("[cyan]Downloading gas station from itch.io (CC0)…[/cyan]")
            from shorts_bot.production.blender.itch_download_cli import download_itch_asset

            download_itch_asset(
                ITCH_GAME_URL,
                rar,
                filename_hint=RAR_NAME,
                headless=True,
            )
        console.print("[cyan]Extracting Gas_station.rar…[/cyan]")
        _extract_rar(rar, DEFAULT_ENV_DIR)

    (DEFAULT_ENV_DIR / "ATTRIBUTION.txt").write_text(ATTRIBUTION_TEXT, encoding="utf-8")

    hit = resolve_environment_model(DEFAULT_ENV_DIR)
    if not hit:
        raise RuntimeError(f"Environment install failed — nothing in {DEFAULT_ENV_DIR}")
    console.print(f"[green]Gas station ready:[/green] {hit}")
    return hit
