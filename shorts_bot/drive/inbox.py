"""Poll Drive inbox folder → import MP4 into draft pack."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.drive.client import DriveFile, download_file, drive_configured, list_mp4s, parse_folder_id
from shorts_bot.invideo.import_cli import import_mp4
from shorts_bot.invideo.script_pack import draft_pack_dir
from shorts_bot.memory.store import MemoryStore

_DRAFT_NAME_RE = re.compile(r"(?:^|[_\-])draft[_\-]?(\d+)", re.I)
_LEADING_NUM_RE = re.compile(r"^(\d+)[_\-\s]")


@dataclass
class InboxPullResult:
    ok: bool
    draft_id: int | None
    file_name: str | None
    video_path: Path | None
    message: str


def _state_path() -> Path:
    return settings.google_drive_state_path


def load_state() -> dict:
    path = _state_path()
    if not path.exists():
        return {"processed_file_ids": [], "assignments": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"processed_file_ids": [], "assignments": {}}
    if not isinstance(data, dict):
        return {"processed_file_ids": [], "assignments": {}}
    data.setdefault("processed_file_ids", [])
    data.setdefault("assignments", {})
    return data


def save_state(state: dict) -> None:
    path = _state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")


def infer_draft_id_from_filename(name: str) -> int | None:
    m = _DRAFT_NAME_RE.search(name)
    if m:
        return int(m.group(1))
    m = _LEADING_NUM_RE.match(name)
    if m:
        return int(m.group(1))
    return None


def draft_needs_video(draft_id: int) -> bool:
    pack = draft_pack_dir(draft_id)
    video = pack / "final_short.mp4"
    return not (video.is_file() and video.stat().st_size > 50_000)


def next_draft_needing_video(store: MemoryStore | None = None) -> int | None:
    store = store or MemoryStore(settings.database_path)
    for status in ("approved", "pending"):
        for draft in store.list_drafts(status=status, limit=30):
            if draft_needs_video(draft.id):
                return draft.id
    return None


def list_inbox_files(*, include_processed: bool = False) -> list[DriveFile]:
    if not drive_configured():
        raise RuntimeError("Drive inbox not configured — set GOOGLE_DRIVE_FOLDER_ID")
    folder_id = parse_folder_id(settings.google_drive_folder_id or "")
    files = list_mp4s(folder_id)
    if include_processed:
        return files
    state = load_state()
    processed = set(state.get("processed_file_ids") or [])
    return [f for f in files if f.file_id not in processed]


def pull_newest(
    *,
    draft_id: int | None = None,
    upload: bool = False,
) -> InboxPullResult:
    """Import newest unprocessed MP4 from Drive inbox into a draft pack."""
    if not drive_configured():
        return InboxPullResult(
            ok=False,
            draft_id=draft_id,
            file_name=None,
            video_path=None,
            message="Drive inbox not configured — see docs/FOR_OWNER_DRIVE_SETUP.md",
        )

    state = load_state()
    processed = set(state.get("processed_file_ids") or [])
    folder_id = parse_folder_id(settings.google_drive_folder_id or "")
    candidates = [f for f in list_mp4s(folder_id) if f.file_id not in processed]
    if not candidates:
        return InboxPullResult(
            ok=False,
            draft_id=draft_id,
            file_name=None,
            video_path=None,
            message="No new MP4 files in Drive inbox folder",
        )

    chosen: DriveFile | None = None
    target_draft = draft_id

    if target_draft is not None:
        chosen = candidates[0]
    else:
        for f in candidates:
            inferred = infer_draft_id_from_filename(f.name)
            if inferred is not None:
                chosen = f
                target_draft = inferred
                break
        if chosen is None:
            target_draft = next_draft_needing_video()
            if target_draft is None:
                return InboxPullResult(
                    ok=False,
                    draft_id=None,
                    file_name=candidates[0].name,
                    video_path=None,
                    message=(
                        f"New file '{candidates[0].name}' in inbox but no draft waiting — "
                        "rename to draft_6.mp4 or run: inbox_cli pull --draft-id N"
                    ),
                )
            chosen = candidates[0]

    assert chosen is not None and target_draft is not None
    pack = draft_pack_dir(target_draft)
    pack.mkdir(parents=True, exist_ok=True)
    tmp = pack / "_drive_inbox_tmp.mp4"
    try:
        download_file(chosen.file_id, tmp)
        video_path = import_mp4(target_draft, tmp)
    finally:
        if tmp.exists():
            tmp.unlink(missing_ok=True)

    processed.add(chosen.file_id)
    state["processed_file_ids"] = sorted(processed)
    assignments = state.setdefault("assignments", {})
    assignments[chosen.file_id] = {
        "draft_id": target_draft,
        "file_name": chosen.name,
        "video_path": str(video_path),
        "at": datetime.now(timezone.utc).isoformat(),
    }
    state["last_poll_at"] = datetime.now(timezone.utc).isoformat()
    save_state(state)

    msg = f"Pulled {chosen.name} → draft {target_draft} ({video_path})"
    if upload:
        from shorts_bot.production.upload_canonical_cli import upload_canonical

        url = upload_canonical(target_draft, video_path)
        msg += f" | PUBLISHED: {url}"
    return InboxPullResult(
        ok=True,
        draft_id=target_draft,
        file_name=chosen.name,
        video_path=video_path,
        message=msg,
    )


def try_pull_for_draft(draft_id: int) -> InboxPullResult | None:
    """Silent poll for workflow — returns None if inbox off or nothing new."""
    if not drive_configured():
        return None
    try:
        from shorts_bot.youtube.google_auth import drive_ready

        if not drive_ready():
            return None
    except Exception:
        return None
    result = pull_newest(draft_id=draft_id, upload=False)
    return result if result.ok else None
