"""YouTube metadata for Peripheral long-form uploads."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from shorts_bot.production.upload_meta import HORROR_BACKEND_TAGS, UploadPackage


@dataclass
class ChapterMarker:
    title: str
    start_seconds: float


def _format_timestamp(seconds: float) -> str:
    total = max(0, int(seconds))
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def chapters_from_manifest(manifest: dict) -> list[ChapterMarker]:
    markers: list[ChapterMarker] = []
    offset = 0.0
    for seg in manifest.get("segments") or []:
        hook = str(seg.get("hook") or seg.get("topic") or "Story").strip()
        title = hook[:80] if hook else f"Story {len(markers) + 1}"
        markers.append(ChapterMarker(title=title, start_seconds=offset))
        offset += float(seg.get("duration_seconds") or 0.0)
    return markers


def format_chapter_block(chapters: list[ChapterMarker]) -> str:
    if not chapters:
        return ""
    lines = ["Chapters:"]
    for ch in chapters:
        lines.append(f"{_format_timestamp(ch.start_seconds)} {ch.title}")
    return "\n".join(lines)


def build_long_compilation_package(
    *,
    story_count: int,
    chapters: list[ChapterMarker],
    hooks: list[str],
) -> UploadPackage:
    """Title + description for stitched Short compilation."""
    count = max(1, story_count)
    title = (
        f"{count} scary stories for people home alone at night | Peripheral"
    )[:100]

    hook_preview = hooks[0].strip() if hooks else ""
    chapter_block = format_chapter_block(chapters)
    description_parts = [
        "🔊 VOLUME WARNING — some stories have jumpscares at the end. Use headphones.",
        hook_preview or "Faceless horror stories from Peripheral.",
        (
            f"Peripheral — {count} scary Shorts stitched for late-night watching. "
            "Same universe, same dread.\n\ndon't blink."
        ),
        chapter_block,
        "AI motion visuals · synthetic media disclosed",
        "#Horror #ScaryStories #HorrorStories #Creepy #Peripheral",
    ]
    description = "\n\n".join(p for p in description_parts if p.strip())

    tags = list(HORROR_BACKEND_TAGS)
    tags.extend(
        [
            "scary stories",
            "horror compilation",
            "horror stories",
            "late night horror",
            "faceless horror",
            "peripheral",
        ]
    )
    seen: set[str] = set()
    deduped: list[str] = []
    for t in tags:
        key = t.lower()
        if key not in seen:
            deduped.append(t)
            seen.add(key)

    checklist = [
        "Visibility: public or unlisted per settings",
        "Format: long_compilation (16:9 blur pillarbox)",
        "Chapters in description for each Short segment",
        "Synthetic media disclosed",
        "No QA build suffix on title",
        "Rotate scare pillar vs last upload",
    ]
    return UploadPackage(
        title=title,
        description=description[:5000],
        tags=deduped[:12],
        visibility="public",
        checklist=checklist,
    )


def write_long_upload_files(
    pack_dir: Path,
    package: UploadPackage,
    *,
    pack_id: str,
) -> Path:
    meta = {
        "pack_id": pack_id,
        "format": "long_compilation",
        "title": package.title,
        "description": package.description,
        "tags": package.tags,
        "visibility": package.visibility,
        "checklist": package.checklist,
    }
    path = pack_dir / "upload_metadata.json"
    path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    md = pack_dir / "UPLOAD_READY.md"
    lines = [
        f"# Long upload ready — {pack_id}",
        "",
        "## Video file",
        "`final_long.mp4`",
        "",
        f"- **Title:** {package.title}",
        "",
        "## Description",
        "```",
        package.description,
        "```",
        "",
        "## Tags",
        ", ".join(package.tags),
    ]
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def package_from_pack_dir(pack_dir: Path) -> UploadPackage:
    manifest_path = pack_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    chapters = chapters_from_manifest(manifest)
    hooks = [str(s.get("hook") or "") for s in manifest.get("segments") or []]
    return build_long_compilation_package(
        story_count=len(manifest.get("segments") or []),
        chapters=chapters,
        hooks=hooks,
    )
