"""Package + schedule a Peripheral Short on YouTube (native publishAt)."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from rich.console import Console

console = Console()

DEFAULT_HOOK = (
    "You pulled over at an empty gas station. "
    "The streetlight flickers. Something too tall is standing by the pumps."
)


def _owner_publish_at(when: str | None, *, hour: int, minute: int) -> datetime:
    tz = ZoneInfo("America/Los_Angeles")
    if when:
        # YYYY-MM-DD or YYYY-MM-DD HH:MM
        raw = when.strip()
        if len(raw) <= 10:
            dt = datetime.strptime(raw, "%Y-%m-%d")
            target = dt.replace(hour=hour, minute=minute, second=0, tzinfo=tz)
        else:
            target = datetime.strptime(raw, "%Y-%m-%d %H:%M").replace(tzinfo=tz)
    else:
        now = datetime.now(tz)
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)
    return target


def _gas_station_description(*, volume_line: str, hook: str) -> str:
    lines = []
    if volume_line.strip():
        lines.append(volume_line.strip())
    lines.extend(
        [
            hook,
            "",
            "Peripheral — scary horror Shorts (~30s). Rural gas station. "
            "Watch to the end.\n\ndon't blink.",
            "",
            "AI motion visuals · synthetic media disclosed",
            "",
            "#Horror #HorrorShorts #Jumpscare #ScaryStories #Creepy #AnalogHorror",
        ]
    )
    return "\n".join(lines)


def schedule_upload(
    draft_id: int,
    video_path: Path,
    *,
    pack_dir: Path | None = None,
    publish_at: datetime | None = None,
    replace_video_id: str | None = None,
    title: str | None = None,
    hook: str | None = None,
) -> str:
    from shorts_bot.config import settings
    from shorts_bot.compliance.upload_guard import record_upload
    from shorts_bot.memory.extensions import MemoryExtensions
    from shorts_bot.memory.store import MemoryStore
    from shorts_bot.production.pack_health import assess_pack_health
    from shorts_bot.production.upload_meta import HORROR_BACKEND_TAGS, write_upload_files
    from shorts_bot.production.upload_meta import UploadPackage
    from shorts_bot.youtube.publish import delete_video
    from shorts_bot.youtube.upload import upload_short
    from shorts_bot.youtube.upload_guardrails import preflight_upload

    if not video_path.is_file():
        raise FileNotFoundError(video_path)

    root = pack_dir or (settings.data_dir / "production" / f"draft_{draft_id}")
    health = assess_pack_health(root, draft_id=draft_id, require_final_short=True)
    if not health.ready_to_upload:
        raise RuntimeError("Pack not upload-ready: " + "; ".join(health.issues))

    store = MemoryStore(settings.database_path)
    mem = MemoryExtensions(store)
    draft = store.get_draft(draft_id)

    if replace_video_id:
        console.print(f"[yellow]Replacing prior upload {replace_video_id}…[/yellow]")
        try:
            console.print(delete_video(replace_video_id))
        except Exception as exc:
            console.print(f"[yellow]YouTube delete skipped: {exc}[/yellow]")
        mem.void_upload_events(video_id=replace_video_id)

    vol = "🔊 VOLUME WARNING — jumpscare at the end. Use headphones."
    hook_line = hook or DEFAULT_HOOK
    upload_title = title or "🔊 Streetlight Flickers — Something Too Tall In The Road"
    upload_title = upload_title[:100]

    package = UploadPackage(
        title=upload_title,
        description=_gas_station_description(volume_line=vol, hook=hook_line),
        tags=list(HORROR_BACKEND_TAGS),
        visibility="public",
        checklist=[
            "Scheduled via YouTube publishAt (private until go-live)",
            "Gas station CC0 environment + Mixamo motion + SCP-096",
            "YPP: max 1 Short per 24h",
            "Synthetic media disclosed",
        ],
    )
    write_upload_files(root, package, draft_id=draft_id)

    if publish_at is None:
        publish_at = _owner_publish_at(None, hour=8, minute=0)

    pre = preflight_upload(
        store,
        mem,
        draft_id=draft_id,
        topic=draft.topic,
        hook=hook_line,
        script=draft.script or hook_line,
        title=upload_title,
        visibility="private",
    )
    if not pre.allowed:
        raise RuntimeError(f"Upload blocked: {pre.message}")

    console.print(
        f"[cyan]Uploading + scheduling[/cyan] draft #{draft_id} → "
        f"{publish_at.astimezone(ZoneInfo('America/Los_Angeles')).strftime('%Y-%m-%d %I:%M %p %Z')}"
    )
    up = upload_short(
        video_path,
        title=upload_title,
        description=package.description,
        tags=package.tags,
        visibility="private",
        publish_at=publish_at,
    )
    record_upload(
        mem,
        draft_id=draft_id,
        topic=draft.topic,
        hook=hook_line,
        script=draft.script or hook_line,
        title=upload_title,
        video_id=up.video_id,
        extra_snapshot={
            "visibility": "scheduled",
            "publish_at": publish_at.isoformat(),
            "source_file": video_path.name,
            "brand": "Peripheral",
            "environment": "gas_station_cc0",
            "backend": "blender",
        },
    )
    mem.schedule_publish(
        video_id=up.video_id,
        draft_id=draft_id,
        visibility="private",
        publish_at=publish_at,
    )

    schedule_path = root / "SCHEDULED.json"
    schedule_path.write_text(
        json.dumps(
            {
                "draft_id": draft_id,
                "video_id": up.video_id,
                "video_url": up.video_url,
                "publish_at_utc": publish_at.astimezone(ZoneInfo("UTC")).isoformat(),
                "publish_at_owner": publish_at.astimezone(
                    ZoneInfo("America/Los_Angeles")
                ).strftime("%Y-%m-%d %I:%M %p %Z"),
                "title": upload_title,
                "video_file": str(video_path),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    md = root / "SCHEDULED.md"
    md.write_text(
        "\n".join(
            [
                f"# Scheduled — draft #{draft_id}",
                "",
                f"- **Goes public:** {publish_at.astimezone(ZoneInfo('America/Los_Angeles')).strftime('%A %B %d, %Y at %I:%M %p %Z')}",
                f"- **YouTube:** {up.video_url}",
                f"- **Video ID:** `{up.video_id}`",
                f"- **Title:** {upload_title}",
                "",
                "YouTube will flip this from private → public automatically at the scheduled time.",
                "",
                f"Local file: `{video_path.name}`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return up.message


def main() -> None:
    parser = argparse.ArgumentParser(description="Schedule Peripheral Short on YouTube")
    parser.add_argument("--draft-id", type=int, required=True)
    parser.add_argument("--video", type=Path, default=None)
    parser.add_argument("--pack-dir", type=Path, default=None)
    parser.add_argument(
        "--at",
        default=None,
        help="Owner-local date/time (America/Los_Angeles), e.g. 2026-06-14 or '2026-06-14 08:00'",
    )
    parser.add_argument("--hour", type=int, default=8, help="Owner-local hour if --at is date-only")
    parser.add_argument("--minute", type=int, default=0)
    parser.add_argument(
        "--replace-video-id",
        default=None,
        help="Delete + void a mistaken prior upload (same draft/title)",
    )
    parser.add_argument("--title", default=None)
    parser.add_argument("--hook", default=None)
    args = parser.parse_args()

    from shorts_bot.config import settings

    pack = args.pack_dir or (settings.data_dir / "production" / f"draft_{args.draft_id}")
    video = args.video or (pack / "final_short.mp4")
    when = _owner_publish_at(args.at, hour=args.hour, minute=args.minute)
    msg = schedule_upload(
        args.draft_id,
        video,
        pack_dir=pack,
        publish_at=when,
        replace_video_id=args.replace_video_id,
        title=args.title,
        hook=args.hook,
    )
    console.print(f"[green]{msg}[/green]")


if __name__ == "__main__":
    main()
