"""Upload canonical render for a draft (public, Peripheral metadata, no QA suffix)."""

from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console

console = Console()


def upload_canonical(
    draft_id: int,
    video_path: Path,
    *,
    pack_dir: Path | None = None,
    volume_warning: bool = True,
) -> str:
    from shorts_bot.config import settings
    from shorts_bot.memory.extensions import MemoryExtensions
    from shorts_bot.memory.store import MemoryStore
    from shorts_bot.production.upload_meta import build_upload_package, write_upload_files
    from shorts_bot.youtube.upload import upload_short
    from shorts_bot.youtube.upload_guardrails import preflight_upload
    from shorts_bot.compliance.upload_guard import record_upload

    if not video_path.exists():
        raise FileNotFoundError(video_path)

    root = pack_dir or (settings.data_dir / "production" / f"draft_{draft_id}")
    store = MemoryStore(settings.database_path)
    mem = MemoryExtensions(store)
    draft = store.get_draft(draft_id)

    package = build_upload_package(draft.topic, draft.hook, draft_id=draft_id)
    title = package.title
    if volume_warning and not title.startswith("🔊"):
        title = f"🔊 {title}"[:100]
    package.title = title
    package.visibility = "public"
    write_upload_files(root, package, draft_id=draft_id)

    pre = preflight_upload(
        store,
        mem,
        draft_id=draft_id,
        topic=draft.topic,
        hook=draft.hook,
        script=draft.script,
        title=title,
        visibility="public",
    )
    if not pre.allowed:
        raise RuntimeError(f"Upload blocked: {pre.message}")

    up = upload_short(
        video_path,
        title=title,
        description=package.description,
        tags=package.tags,
        visibility="public",
    )
    record_upload(
        mem,
        draft_id=draft_id,
        topic=draft.topic,
        hook=draft.hook,
        script=draft.script,
        title=title,
        video_id=up.video_id,
        extra_snapshot={
            "visibility": "public",
            "source_file": video_path.name,
            "brand": "Rapid Tool Review",
            "canonical": True,
        },
    )
    if settings.post_upload_analytics_sync:
        from shorts_bot.youtube.post_upload import sync_analytics_after_upload

        sync_analytics_after_upload()
    return up.video_url


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload canonical Peripheral Short (public)")
    parser.add_argument("--draft-id", type=int, required=True)
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--pack-dir", type=Path, default=None)
    parser.add_argument("--no-volume-prefix", action="store_true")
    args = parser.parse_args()
    url = upload_canonical(
        args.draft_id,
        args.video,
        pack_dir=args.pack_dir,
        volume_warning=not args.no_volume_prefix,
    )
    console.print(f"[green]Uploaded: {url}[/green]")


if __name__ == "__main__":
    main()
