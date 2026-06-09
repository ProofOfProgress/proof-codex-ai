from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.memory.store import MemoryStore
from shorts_bot.production.image_prompts import build_image_briefs, build_master_prompt
from shorts_bot.production.turboscribe_parser import parse_turboscribe


@dataclass
class ProductionPack:
    draft_id: int
    topic: str
    output_dir: Path
    image_count: int
    manifest_path: Path
    message: str


def _capcut_instructions(briefs: list, topic: str) -> str:
    lines = [
        f"# CapCut timeline — {topic}",
        "",
        "1. Import voiceover audio track.",
        "2. Import all images from `images/` (or generate from `prompts/` first).",
        "3. Place each image at its **start** second; drag end to the **next** image start.",
        "",
        "| Start | End | File | Spoken |",
        "|-------|-----|------|--------|",
    ]
    for b in briefs:
        lines.append(
            f"| {b.start_seconds:.0f}s | {b.end_seconds:.0f}s | `{b.filename_stem}.png` | {b.spoken_text[:60]}… |"
            if len(b.spoken_text) > 60
            else f"| {b.start_seconds:.0f}s | {b.end_seconds:.0f}s | `{b.filename_stem}.png` | {b.spoken_text} |"
        )
    lines.extend(
        [
            "",
            "4. Add captions (optional — TurboScribe SRT also works).",
            "5. Music: YouTube Audio Library, duck under voice.",
            "6. Export 1080×1920 H.264 → YouTube Short.",
        ]
    )
    return "\n".join(lines)


def build_production_pack(
    store: MemoryStore,
    *,
    draft_id: int,
    turboscribe_text: str,
    output_root: Path | None = None,
) -> ProductionPack:
    draft = store.get_draft(draft_id)
    segments = parse_turboscribe(turboscribe_text)
    if not segments:
        raise ValueError(
            "No timestamps found. Paste TurboScribe export with lines like '0:07 your words...'"
        )

    briefs = build_image_briefs(segments, topic=draft.topic)
    root = output_root or (settings.data_dir / "production" / f"draft_{draft_id}")
    root.mkdir(parents=True, exist_ok=True)
    prompts_dir = root / "prompts"
    images_dir = root / "images"
    prompts_dir.mkdir(exist_ok=True)
    images_dir.mkdir(exist_ok=True)

    for b in briefs:
        (prompts_dir / f"{b.filename_stem}.txt").write_text(b.prompt, encoding="utf-8")

    manifest = {
        "draft_id": draft_id,
        "topic": draft.topic,
        "hook": draft.hook,
        "script": draft.script,
        "workflow": "turboscribe_timestamps_to_still_images",
        "image_count": len(briefs),
        "segments": [
            {
                "start_seconds": b.start_seconds,
                "end_seconds": b.end_seconds,
                "filename": f"{b.filename_stem}.png",
                "spoken_text": b.spoken_text,
                "prompt_file": f"prompts/{b.filename_stem}.txt",
            }
            for b in briefs
        ],
    }
    manifest_path = root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    (root / "MASTER_IMAGE_PROMPT.md").write_text(
        build_master_prompt() + "\n\n---\n\n## Timestamped script\n\n"
        + "\n".join(f"{s.label} {s.text}" for s in segments),
        encoding="utf-8",
    )
    (root / "CAPCUT_TIMELINE.md").write_text(_capcut_instructions(briefs, draft.topic), encoding="utf-8")
    (root / "README.txt").write_text(
        "Soft Continuity production pack\n\n"
        "1. Record voiceover from script in manifest.json\n"
        "2. Upload audio to TurboScribe → copy timestamped text → re-run produce if needed\n"
        "3. Generate images: one per prompts/*.txt (Cursor, Higgsfield, or manual)\n"
        "4. Save PNGs to images/ named like 00.07.png\n"
        "5. Follow CAPCUT_TIMELINE.md\n",
        encoding="utf-8",
    )

    return ProductionPack(
        draft_id=draft_id,
        topic=draft.topic,
        output_dir=root,
        image_count=len(briefs),
        manifest_path=manifest_path,
        message=(
            f"Production pack ready: {len(briefs)} images for '{draft.topic}'. "
            f"Folder: {root}. Generate PNGs from prompts/, then edit in CapCut."
        ),
    )
