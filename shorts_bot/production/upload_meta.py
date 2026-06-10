"""YouTube upload metadata — optimized for reach without spam signals."""

from __future__ import annotations

import json
import re
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
    """Conservative metadata: helpful title, no clickbait."""
    from shorts_bot.config import settings
    from shorts_bot.production.niche import NICHE_NAME

    title = _safe_title(topic, hook)
    description = _safe_description(topic)
    tags = [
        "calm shorts",
        "anxiety help",
        "self help shorts",
        "mental health tips",
        "soft continuity",
        "the minute before",
    ]
    visibility = settings.youtube_upload_visibility
    if visibility not in ("public", "unlisted", "private"):
        visibility = "unlisted"

    checklist = [
        f"Visibility: {visibility}",
        f"Niche: {NICHE_NAME}",
        "One Short today only — no batch spam (shadowban / inauthentic signal)",
        "Title is helpful, not rage-bait or ALL CAPS shock",
        "Captions in Jenny 05 safe zone — above Shorts title overlay",
        "After publish: run sync in bot for analytics learning",
        "If retention is weak, tweak hook — do not re-upload duplicate same day",
        "Reply to first comments manually (engagement signal)",
    ]
    return UploadPackage(
        title=title,
        description=description,
        tags=tags,
        visibility=visibility,
        checklist=checklist,
    )


def _safe_title(topic: str, hook: str) -> str:
    t = topic.strip().lower()
    if "minute before" in t:
        moment = re.sub(r"^the minute before\s+", "", t, flags=re.I).strip()
        if moment:
            return f"Before {moment[:55]} — do this first #Shorts"[:100]
    if hook and len(hook) < 70 and "stop scrolling" not in hook.lower():
        return hook[:95]
    return f"Before {topic[:60]} — one thing that helped me #Shorts"[:100]


def _safe_description(topic: str) -> str:
    return (
        "The Minute Before — one moment, one fix.\n\n"
        f"Tonight: {topic}\n"
        "Faceless calm Shorts for overloaded days.\n\n"
        "Soft Continuity — you're still here. Good.\n\n"
        "#Shorts #calm #selfhelp"
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
