"""Auto-download SCP-096 mesh — no owner handoff required.

Source: SCP - Containment Breach Ultimate Edition (CC BY-SA 3.0)
https://github.com/Jabka666/scpcb-ue-my
"""

from __future__ import annotations

import shutil
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

from rich.console import Console

from shorts_bot.production.blender.creature_paths import SCP096_DIR, resolve_creature_model

console = Console()

GITHUB_RAW = (
    "https://raw.githubusercontent.com/Jabka666/scpcb-ue-my/main/GFX/NPCs"
)
SCP096_FILES = (
    ("scp_096.b3d", f"{GITHUB_RAW}/scp_096.b3d"),
    ("scp_096.png", f"{GITHUB_RAW}/scp_096.png"),
)

ATTRIBUTION_TEXT = """SCP-096 creature mesh
Source: SCP - Containment Breach Ultimate Edition Reborn
Repository: https://github.com/Jabka666/scpcb-ue-my
License: Creative Commons Attribution-ShareAlike 3.0
https://creativecommons.org/licenses/by-sa/3.0/

Original SCP-096 by SCP Foundation community (CC BY-SA).
Used as Peripheral Form 2 base mesh — retextured/darkened in render pipeline.
"""


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "ShortsBot/1.0 (Blender pipeline)"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = resp.read()
    if len(data) < 1000:
        raise RuntimeError(f"Download too small ({len(data)} bytes): {url}")
    dest.write_bytes(data)


def _assimp_available() -> bool:
    return shutil.which("assimp") is not None


def _convert_b3d_to_glb(b3d: Path, glb: Path) -> Path:
    if not _assimp_available():
        raise RuntimeError(
            "assimp CLI missing — run: sudo apt-get install -y assimp-utils"
        )
    glb.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        ["assimp", "export", str(b3d), str(glb)],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0 or not glb.is_file() or glb.stat().st_size < 5000:
        raise RuntimeError(
            f"assimp export failed:\n{(proc.stderr or proc.stdout)[-1500:]}"
        )
    return glb


def ensure_scp096_model(*, force: bool = False) -> Path:
    """Download + convert SCP-096 if missing. Returns path to scp_096.glb."""
    existing = resolve_creature_model(SCP096_DIR)
    if existing and not force and existing.stat().st_size > 5000:
        if existing.suffix.lower() != ".b3d":
            return existing

    SCP096_DIR.mkdir(parents=True, exist_ok=True)
    console.print("[cyan]Downloading SCP-096 from GitHub (CC BY-SA)…[/cyan]")

    b3d = SCP096_DIR / "scp_096.b3d"
    for name, url in SCP096_FILES:
        dest = SCP096_DIR / name
        if force or not dest.is_file() or dest.stat().st_size < 1000:
            try:
                _download(url, dest)
                console.print(f"  [green]✓[/green] {name}")
            except (urllib.error.URLError, RuntimeError) as exc:
                raise RuntimeError(f"Failed to download {name} from {url}: {exc}") from exc

    (SCP096_DIR / "ATTRIBUTION.txt").write_text(ATTRIBUTION_TEXT, encoding="utf-8")

    glb = SCP096_DIR / "scp_096.glb"
    fbx = SCP096_DIR / "scp_096.fbx"
    if force or not glb.is_file() or glb.stat().st_size < 5000:
        console.print("[cyan]Converting B3D → GLB (assimp)…[/cyan]")
        _convert_b3d_to_glb(b3d, glb)
    if force or not fbx.is_file() or fbx.stat().st_size < 5000:
        _convert_b3d_to_glb(b3d, fbx)

    hit = resolve_creature_model(SCP096_DIR)
    if not hit:
        raise RuntimeError(f"Creature install failed — nothing in {SCP096_DIR}")
    console.print(f"[green]SCP-096 ready:[/green] {hit}")
    return hit
