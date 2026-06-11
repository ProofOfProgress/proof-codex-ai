"""Render + upload unlisted horror Short (SFX QA / owner preview)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rich.console import Console

console = Console()


def upload_existing_video(
    draft_id: int,
    video_path: Path,
    *,
    pack_dir: Path | None = None,
    title_suffix: str = "",
    allow_duplicate_draft: bool = True,
) -> str:
    """Upload an already-rendered MP4 as unlisted (no re-render)."""
    from shorts_bot.config import settings
    from shorts_bot.memory.store import MemoryStore
    from shorts_bot.memory.extensions import MemoryExtensions
    from shorts_bot.production.upload_meta import build_upload_package, write_upload_files
    from shorts_bot.youtube.upload import upload_short
    from shorts_bot.youtube.upload_guardrails import preflight_upload
    from shorts_bot.compliance.upload_guard import record_upload

    root = pack_dir or (settings.data_dir / "production" / f"draft_{draft_id}")
    if not video_path.exists():
        raise FileNotFoundError(video_path)

    store = MemoryStore(settings.database_path)
    draft = store.get_draft(draft_id)
    package = build_upload_package(draft.topic, draft.hook, draft_id=draft_id)
    title = package.title
    if title_suffix and title_suffix not in title:
        title = f"{title} {title_suffix}".strip()[:100]
    package.visibility = "unlisted"
    write_upload_files(root, package, draft_id=draft_id)

    mem = MemoryExtensions(store)
    pre = preflight_upload(
        store,
        mem,
        draft_id=draft_id,
        topic=draft.topic,
        hook=draft.hook,
        script=draft.script,
        title=title,
        allow_duplicate_draft=allow_duplicate_draft,
        visibility="unlisted",
    )
    if not pre.allowed:
        raise RuntimeError(f"Upload blocked: {pre.message}")

    up = upload_short(
        video_path,
        title=title,
        description=package.description,
        tags=package.tags,
        visibility="unlisted",
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
            "visibility": "unlisted",
            "qa_sfx_upload": True,
            "source_file": video_path.name,
        },
    )
    return f"Unlisted upload OK: {up.video_url}"


def upload_unlisted_draft(
    draft_id: int,
    *,
    pack_dir: Path | None = None,
    output_name: str = "final_short_unlisted.mp4",
    title_suffix: str = "",
    allow_duplicate_draft: bool = False,
    video_path: Path | None = None,
    render: bool = True,
) -> str:
    from shorts_bot.config import settings
    from shorts_bot.memory.store import MemoryStore
    from shorts_bot.memory.extensions import MemoryExtensions
    from shorts_bot.production.jumpscare_timing import plan_for_draft, persist_plan
    from shorts_bot.production.render_video import render_short_video
    from shorts_bot.production.upload_meta import build_upload_package, write_upload_files
    from shorts_bot.youtube.upload import upload_short
    from shorts_bot.youtube.upload_guardrails import preflight_upload
    from shorts_bot.compliance.upload_guard import record_upload

    root = pack_dir or (settings.data_dir / "production" / f"draft_{draft_id}")
    manifest_path = root / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"No pack at {root}")

    if video_path and video_path.exists() and not render:
        return upload_existing_video(
            draft_id,
            video_path,
            pack_dir=root,
            title_suffix=title_suffix,
            allow_duplicate_draft=allow_duplicate_draft,
        )

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    segments = manifest.get("segments") or []
    scare_plan = plan_for_draft(draft_id, len(segments))
    if draft_id % 3 == 0:
        # Owner QA: force finale jumpscare for SFX validation upload
        from shorts_bot.production.jumpscare_timing import JumpscarePlan

        last = max(0, len(segments) - 1)
        scare_plan = JumpscarePlan(
            profile="finale",
            primary_segment_index=last,
            decoy_segment_index=None,
            has_jumpscare=True,
            sting_start_ratio=0.92,
            volume_warning="🔊 VOLUME WARNING — jumpscare at the end. Use headphones.",
            creator_note="QA upload — finale scare + agent-mixed SFX.",
        )
    manifest["jumpscare_plan"] = scare_plan.to_dict()
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    persist_plan(draft_id, scare_plan)

    console.print(f"[cyan]Rendering draft #{draft_id} with horror SFX + finale scare…[/cyan]")
    rendered = render_short_video(
        root,
        draft_id=draft_id,
        output_name=output_name,
    )
    console.print(f"[green]{rendered.message}[/green]")

    store = MemoryStore(settings.database_path)
    draft = store.get_draft(draft_id)
    package = build_upload_package(draft.topic, draft.hook, draft_id=draft_id)
    title = package.title
    if title_suffix and title_suffix not in title:
        title = f"{title} {title_suffix}".strip()[:100]
    package.visibility = "unlisted"

    write_upload_files(root, package, draft_id=draft_id)

    mem = MemoryExtensions(store)
    pre = preflight_upload(
        store,
        mem,
        draft_id=draft_id,
        topic=draft.topic,
        hook=draft.hook,
        script=draft.script,
        title=title,
        allow_duplicate_draft=allow_duplicate_draft,
        visibility="unlisted",
    )
    if not pre.allowed:
        raise RuntimeError(f"Upload blocked: {pre.message}")

    up = upload_short(
        rendered.output_path,
        title=title,
        description=package.description,
        tags=package.tags,
        visibility="unlisted",
    )
    record_upload(
        mem,
        draft_id=draft_id,
        topic=draft.topic,
        hook=draft.hook,
        script=draft.script,
        title=title,
        video_id=up.video_id,
        extra_snapshot={"visibility": "unlisted", "qa_sfx_upload": True},
    )
    return f"Unlisted upload OK: {up.video_url}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Render + upload unlisted Don't Blink Short")
    parser.add_argument("--draft-id", type=int, required=True)
    parser.add_argument("--pack-dir", type=Path, default=None)
    parser.add_argument("--title-suffix", type=str, default="")
    parser.add_argument(
        "--allow-duplicate-draft",
        action="store_true",
        help="Re-upload same draft_id with a unique title suffix (QA)",
    )
    parser.add_argument("--video", type=Path, default=None, help="Upload this MP4 (skip render)")
    parser.add_argument(
        "--no-render",
        action="store_true",
        help="With --video: upload existing file without re-rendering",
    )
    args = parser.parse_args()
    console.print(
        upload_unlisted_draft(
            args.draft_id,
            pack_dir=args.pack_dir,
            title_suffix=args.title_suffix,
            allow_duplicate_draft=args.allow_duplicate_draft,
            video_path=args.video,
            render=not args.no_render,
        )
    )


if __name__ == "__main__":
    main()
