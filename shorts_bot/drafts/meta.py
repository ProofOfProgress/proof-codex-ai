"""Per-draft sidecar metadata (visual_beats, variety seed) — no DB migration needed."""

from __future__ import annotations

import json
from pathlib import Path

from shorts_bot.config import settings


def _meta_path(draft_id: int) -> Path:
    root = settings.data_dir / "draft_meta"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"draft_{draft_id}.json"


def load_draft_meta(draft_id: int) -> dict:
    path = _meta_path(draft_id)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_draft_meta(draft_id: int, **fields) -> dict:
    data = load_draft_meta(draft_id)
    data.update({k: v for k, v in fields.items() if v is not None})
    path = _meta_path(draft_id)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def visual_beats_for_draft(draft_id: int) -> list[str]:
    beats = load_draft_meta(draft_id).get("visual_beats") or []
    return [str(b).strip() for b in beats if str(b).strip()]
