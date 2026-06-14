"""Gas-station environment paths — no bpy (safe in tests/CLI)."""

from __future__ import annotations

from pathlib import Path

DEFAULT_ENV_DIR = Path("channel/assets/environments/gas_station")
GAS_STATION_FBX = DEFAULT_ENV_DIR / "Gas_station" / "Models" / "Gas_station.fbx"
GAS_STATION_PROPS = DEFAULT_ENV_DIR / "Gas_station" / "Models" / "Gas_station_Props.fbx"
GAS_STATION_CANDIDATES = (
    GAS_STATION_FBX,
    DEFAULT_ENV_DIR / "gas_station.fbx",
    DEFAULT_ENV_DIR / "gas_station.glb",
    DEFAULT_ENV_DIR / "Gas_station.fbx",
)


def resolve_environment_model(explicit: str | Path | None = None) -> Path | None:
    """First existing environment mesh — explicit path, env, or default gas-station slot."""
    if explicit:
        p = Path(explicit)
        if p.is_file():
            return p
        if p.is_dir():
            for name in (
                "Gas_station.fbx",
                "gas_station.fbx",
                "gas_station.glb",
                "environment.fbx",
                "scene.fbx",
            ):
                hit = p / name
                if hit.is_file():
                    return hit
            nested = p / "Gas_station" / "Models" / "Gas_station.fbx"
            if nested.is_file():
                return nested
            return None
        return None
    for candidate in GAS_STATION_CANDIDATES:
        if candidate.is_file():
            return candidate
    return None


def environment_model_status(explicit: str | Path | None = None) -> dict:
    resolved = resolve_environment_model(explicit)
    return {
        "resolved": str(resolved) if resolved else None,
        "expected_dir": str(DEFAULT_ENV_DIR),
        "candidates_checked": [str(c) for c in GAS_STATION_CANDIDATES],
    }
