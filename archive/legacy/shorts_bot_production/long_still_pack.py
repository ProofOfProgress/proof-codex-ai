"""Scaffold production pack for long_still narrative (16:9 Ken Burns)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from shorts_bot.config import settings


@dataclass
class LongStillPack:
    draft_id: int
    pack_dir: Path
    manifest_path: Path
    beat_count: int
    message: str


def scaffold_long_still_pack(
    *,
    draft_id: int,
    outline_path: Path | None = None,
    target_beats: int = 16,
    output_root: Path | None = None,
) -> LongStillPack:
    """Create directories + manifest for long_still without generating images."""
    from shorts_bot.memory.store import MemoryStore

    store = MemoryStore(settings.database_path)
    draft = store.get_draft(draft_id)
    root = output_root or (settings.data_dir / "production" / f"draft_{draft_id}_long_still")
    root.mkdir(parents=True, exist_ok=True)

    for sub in ("images", "prompts", "clips", "audio"):
        (root / sub).mkdir(exist_ok=True)

    sections: list[dict] = []
    word_count = 0
    if outline_path and outline_path.is_file():
        data = json.loads(outline_path.read_text(encoding="utf-8"))
        sections = data.get("sections") or []
        word_count = int(data.get("word_count_estimate") or 0)

    if not sections:
        sections = [{"id": "beat_0", "label": "Segment", "beats": draft.hook}]

    beats_per_section = max(2, target_beats // max(1, len(sections)))
    beats: list[dict] = []
    t = 0.0
    seg_dur = 35.0
    for i, sec in enumerate(sections):
        for j in range(beats_per_section):
            beats.append(
                {
                    "index": len(beats),
                    "section_id": sec.get("id", f"sec_{i}"),
                    "label": sec.get("label", ""),
                    "spoken_text": sec.get("beats", "")[:200],
                    "start_seconds": round(t, 2),
                    "end_seconds": round(t + seg_dur, 2),
                    "filename": f"beat_{len(beats):03d}.png",
                    "aspect_ratio": "16:9",
                    "motion": "ken_burns",
                }
            )
            t += seg_dur

    if not beats:
        for i in range(target_beats):
            beats.append(
                {
                    "index": i,
                    "spoken_text": draft.hook if i == 0 else f"[expand segment {i}]",
                    "start_seconds": round(i * seg_dur, 2),
                    "end_seconds": round((i + 1) * seg_dur, 2),
                    "filename": f"beat_{i:03d}.png",
                    "aspect_ratio": "16:9",
                    "motion": "ken_burns",
                }
            )

    manifest = {
        "format": "long_still",
        "draft_id": draft_id,
        "topic": draft.topic,
        "hook": draft.hook,
        "script": draft.script,
        "aspect_ratio": "16:9",
        "target_duration_seconds": [300, 720],
        "max_i2v_beats": 0,
        "word_count": word_count,
        "beats": beats,
        "segments": beats,
        "output_video": "final_long.mp4",
    }
    manifest_path = root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    (root / "VOICEOVER_SCRIPT.txt").write_text(
        f"HOOK: {draft.hook}\n\n"
        f"[Expand to 800–1400 words from SHORT_SCRIPT below]\n\n"
        f"{draft.script}\n",
        encoding="utf-8",
    )

    return LongStillPack(
        draft_id=draft_id,
        pack_dir=root,
        manifest_path=manifest_path,
        beat_count=len(beats),
        message=f"long_still scaffold at {root} — {len(beats)} beats, 16:9 stills",
    )
