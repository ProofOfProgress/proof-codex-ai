"""Production pack — script files for InVideo (no homemade render)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.memory.store import MemoryStore
from shorts_bot.production.legacy_retired import LegacyPipelineRetired


@dataclass
class ProductionPack:
    draft_id: int
    topic: str
    output_dir: Path
    image_count: int
    images_rendered: int
    manifest_path: Path
    message: str


def build_production_pack(
    store: MemoryStore,
    *,
    draft_id: int,
    turboscribe_text: str = "",
    output_root: Path | None = None,
    auto_from_script: bool = False,
    render_images: bool = False,
) -> ProductionPack:
    """Write script/hook files under data/production/draft_N for InVideo handoff."""
    if render_images or auto_from_script:
        raise LegacyPipelineRetired("render_images/auto_from_script no longer supported")

    draft = store.get_draft(draft_id)
    from shorts_bot.invideo.script_pack import draft_pack_dir

    root = output_root or draft_pack_dir(draft_id)
    root.mkdir(parents=True, exist_ok=True)
    (root / "script.txt").write_text(draft.script or "", encoding="utf-8")
    (root / "hook.txt").write_text(draft.hook or "", encoding="utf-8")
    if turboscribe_text.strip():
        (root / "transcript.txt").write_text(turboscribe_text.strip(), encoding="utf-8")

    manifest = {
        "draft_id": draft_id,
        "topic": draft.topic,
        "backend": "invideo",
        "render_mode": "invideo",
        "message": "Export MP4 via invideo ship_cli or owner Drive → fetch_url_cli",
    }
    manifest_path = root / "pack_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return ProductionPack(
        draft_id=draft_id,
        topic=draft.topic,
        output_dir=root,
        image_count=0,
        images_rendered=0,
        manifest_path=manifest_path,
        message=manifest["message"],
    )


def build_pack_from_script_timing(
    store: MemoryStore,
    draft_id: int,
    *,
    output_root: Path | None = None,
) -> ProductionPack:
    return build_production_pack(store, draft_id=draft_id, output_root=output_root)
