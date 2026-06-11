"""Content stamps — invalidate stale VO/I2V when script changes."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def content_digest(hook: str, script: str) -> str:
    payload = f"{hook.strip()}\n{script.strip()}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def stamp_path(pack_dir: Path) -> Path:
    return pack_dir / "content_stamp.json"


def write_content_stamp(pack_dir: Path, *, hook: str, script: str) -> Path:
    pack_dir.mkdir(parents=True, exist_ok=True)
    path = stamp_path(pack_dir)
    path.write_text(
        json.dumps({"digest": content_digest(hook, script)}, indent=2),
        encoding="utf-8",
    )
    return path


def content_stamp_stale(pack_dir: Path, *, hook: str, script: str) -> bool:
    path = stamp_path(pack_dir)
    if not path.exists():
        return True
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return str(data.get("digest") or "") != content_digest(hook, script)
    except json.JSONDecodeError:
        return True


def invalidate_downstream_steps(pack_dir: Path, draft_id: int) -> None:
    from shorts_bot.production.pipeline_state import load_state, save_state

    state = load_state(pack_dir, draft_id)
    for step in (
        "humanize",
        "voiceover",
        "transcript",
        "pack",
        "render",
        "video_qc",
        "vision_qc",
        "metadata",
        "upload",
    ):
        state.steps.pop(step, None)
    save_state(pack_dir, state)


def clear_render_artifacts(pack_dir: Path) -> list[str]:
    """Remove downstream artifacts when script/content changed."""
    removed: list[str] = []
    for name in (
        "voiceover.mp3",
        "voiceover_stamp.json",
        "transcript.txt",
        "turboscribe_transcript.txt",
        "transcript_stamp.json",
        "manifest.json",
        "final_short.mp4",
    ):
        p = pack_dir / name
        if p.exists():
            p.unlink()
            removed.append(name)
    for sub in ("clips", "images"):
        d = pack_dir / sub
        if d.is_dir():
            for f in d.glob("*"):
                if f.is_file():
                    f.unlink()
                    removed.append(f"{sub}/{f.name}")
    return removed
