"""YouTube upload metadata — optimized for reach without spam signals."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class UploadPackage:
    title: str
    description: str
    tags: list[str]
    visibility: str
    checklist: list[str]


def build_upload_package(topic: str, hook: str, *, draft_id: int) -> UploadPackage:
    """Conservative metadata: helpful title, no clickbait, unlisted first."""
    title = _safe_title(topic, hook)
    description = _safe_description(topic)
    tags = [
        "sleep tips",
        "insomnia help",
        "3am anxiety",
        "calm",
        "self help shorts",
        "soft continuity",
    ]
    checklist = [
        "Upload as UNLISTED first — watch retention 24h before going public",
        "One Short today only — no batch spam (shadowban / inauthentic signal)",
        "Title is helpful, not rage-bait or ALL CAPS shock",
        "No misleading thumbnail text (images are calm stills — good)",
        "After publish: run sync in bot for analytics learning",
        "If retention is weak, tweak hook — do not re-upload duplicate same day",
        "Reply to first comments manually (engagement signal)",
    ]
    return UploadPackage(
        title=title,
        description=description,
        tags=tags,
        visibility="unlisted",
        checklist=checklist,
    )


def _safe_title(topic: str, hook: str) -> str:
    t = topic.strip().lower()
    if "3" in t and "sleep" in t:
        return "When You Wake at 3AM — Do This Before Your Phone"
    if hook and len(hook) < 70 and "stop scrolling" not in hook.lower():
        return hook[:95]
    return f"A small fix for {topic} #Shorts"[:100]


def _safe_description(topic: str) -> str:
    return (
        "Small fixes for heavy days.\n\n"
        f"Tonight: {topic} — one thing to try when your mind won't switch off.\n\n"
        "Soft Continuity — calm, faceless Shorts. Sleep, focus, boundaries.\n"
        "You're still here. Good.\n\n"
        "#Shorts #sleep #calm"
    )


def write_upload_files(pack_dir: Path, package: UploadPackage, *, draft_id: int) -> Path:
    meta = {
        "draft_id": draft_id,
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
        f"# Upload ready — draft {draft_id}",
        "",
        "## Video file",
        "`final_short.mp4`",
        "",
        "## Recommended settings (anti-spam / YPP-safe)",
        f"- **Visibility:** {package.visibility} (switch to Public after 24h if retention looks OK)",
        f"- **Title:** {package.title}",
        "",
        "## Description",
        "```",
        package.description,
        "```",
        "",
        "## Tags",
        ", ".join(package.tags),
        "",
        "## Checklist",
    ]
    lines.extend(f"- {c}" for c in package.checklist)
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
