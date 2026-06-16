"""Production pack health — validate clips/stills before render or upload."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

RenderSource = Literal["clip", "still", "missing"]


@dataclass(frozen=True)
class SegmentHealth:
    index: int
    stem: str
    filename: str
    has_clip: bool
    has_still: bool
    render_source: RenderSource
    spoken_preview: str = ""


@dataclass
class PackHealthReport:
    draft_id: int
    pack_dir: Path
    segment_count: int = 0
    clip_count: int = 0
    still_fallback_count: int = 0
    missing_segment_count: int = 0
    ready_to_render: bool = False
    ready_to_upload: bool = False
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    segments: list[SegmentHealth] = field(default_factory=list)

    def summary_lines(self) -> list[str]:
        status = "OK" if self.ready_to_render else "BLOCKED"
        lines = [
            f"Pack draft #{self.draft_id} — {status}",
            f"  segments: {self.segment_count} | clips: {self.clip_count} | "
            f"still fallbacks: {self.still_fallback_count} | missing: {self.missing_segment_count}",
        ]
        for issue in self.issues:
            lines.append(f"  [issue] {issue}")
        for warn in self.warnings:
            lines.append(f"  [warn] {warn}")
        return lines


def _min_clip_bytes() -> int:
    return 5000


def assess_pack_health(
    pack_dir: Path,
    *,
    draft_id: int,
    require_final_short: bool = False,
    final_short_name: str = "final_short.mp4",
) -> PackHealthReport:
    """Check manifest segments resolve to clips or stills; flag gaps before render."""
    report = PackHealthReport(draft_id=draft_id, pack_dir=pack_dir)
    manifest_path = pack_dir / "manifest.json"
    if not manifest_path.exists():
        report.issues.append(f"Missing manifest.json at {manifest_path}")
        return report

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        report.issues.append(f"Invalid manifest.json: {exc}")
        return report

    segments = manifest.get("segments") or []
    if not segments:
        report.issues.append("Manifest has no segments")
        return report

    render_mode = manifest.get("render_mode") or ""
    clips_dir = pack_dir / "clips"
    if render_mode in ("blender_clips", "kling_clips"):
        import re

        prefix = "blender_part_" if render_mode == "blender_clips" else "kling_part_"
        pattern = re.compile(rf"{re.escape(prefix)}\d{{2}}\.mp4$")
        motion_clips = sorted(p for p in clips_dir.glob(f"{prefix}*.mp4") if pattern.fullmatch(p.name))
        min_bytes = _min_clip_bytes()
        if len(motion_clips) < 1:
            report.issues.append(f"No {render_mode} clips in {clips_dir}")
        else:
            for clip in motion_clips:
                if clip.stat().st_size < min_bytes:
                    report.issues.append(f"Clip too small: {clip.name}")
            report.clip_count = len(motion_clips)
        from shorts_bot.production.launch_phase import is_silent_launch_draft

        if not is_silent_launch_draft(draft_id):
            audio_path = pack_dir / "voiceover.mp3"
            if not audio_path.is_file():
                report.issues.append(f"Missing voiceover at {audio_path}")
        report.segment_count = len(segments)
        report.ready_to_render = not report.issues
        final_path = pack_dir / final_short_name
        if require_final_short and not final_path.is_file():
            report.issues.append(f"Missing rendered video at {final_path.name}")
            report.ready_to_upload = False
        else:
            report.ready_to_upload = report.ready_to_render and (
                final_path.is_file() if require_final_short else report.ready_to_render
            )
        return report

    report.segment_count = len(segments)
    images_dir = pack_dir / "images"
    min_bytes = _min_clip_bytes()

    for i, seg in enumerate(segments):
        filename = str(seg.get("filename") or "").strip()
        if not filename:
            report.issues.append(f"Segment {i}: missing filename")
            continue
        stem = Path(filename).stem
        clip_path = clips_dir / f"{stem}.mp4"
        still_path = images_dir / filename
        has_clip = clip_path.is_file() and clip_path.stat().st_size >= min_bytes
        has_still = still_path.is_file() and still_path.stat().st_size > 0

        if has_clip:
            source: RenderSource = "clip"
            report.clip_count += 1
        elif has_still:
            source = "still"
            report.still_fallback_count += 1
            report.warnings.append(
                f"Segment {i} ({stem}): no clip — render will use still {filename}"
            )
        else:
            source = "missing"
            report.missing_segment_count += 1
            report.issues.append(
                f"Segment {i} ({stem}): missing clip {clip_path.name} and still {filename}"
            )

        spoken = str(seg.get("spoken_text") or "")[:72]
        report.segments.append(
            SegmentHealth(
                index=i,
                stem=stem,
                filename=filename,
                has_clip=has_clip,
                has_still=has_still,
                render_source=source,
                spoken_preview=spoken,
            )
        )

    audio_path = pack_dir / "voiceover.mp3"
    if not audio_path.is_file():
        report.issues.append(f"Missing voiceover at {audio_path}")

    hook = str(manifest.get("hook") or "")
    script = str(manifest.get("script") or "")
    if hook or script:
        from shorts_bot.production.pipeline_integrity import content_stamp_stale

        if content_stamp_stale(pack_dir, hook=hook, script=script):
            report.warnings.append(
                "content_stamp.json stale — script changed since last VO/I2V stamp"
            )

    from shorts_bot.config import settings
    from shorts_bot.production.jumpscare_timing import (
        JumpscarePlan,
        load_plan_for_draft,
    )

    plan_raw = manifest.get("jumpscare_plan")
    plan = (
        JumpscarePlan.from_dict(plan_raw)
        if plan_raw
        else load_plan_for_draft(draft_id, len(segments))
    )
    if plan.has_jumpscare and settings.jumpscare_dedicated_clip:
        from shorts_bot.production.jumpscare_clip import jumpscare_clip_path

        scare = jumpscare_clip_path(clips_dir)
        if not scare.is_file() or scare.stat().st_size < min_bytes:
            report.issues.append(
                f"Missing dedicated jumpscare clip at {scare.name} "
                "(required when jumpscare_dedicated_clip=true)"
            )

    report.ready_to_render = not report.issues
    final_path = pack_dir / final_short_name
    if require_final_short and not final_path.is_file():
        report.issues.append(f"Missing rendered video at {final_path.name}")
        report.ready_to_upload = False
    else:
        report.ready_to_upload = report.ready_to_render and (
            final_path.is_file() if require_final_short else report.ready_to_render
        )

    if report.still_fallback_count and report.ready_to_render:
        report.warnings.append(
            f"{report.still_fallback_count} segment(s) will render as still Ken Burns — "
            "re-run regen when AI_VIDEO_GENERATION_ENABLED=true"
        )

    return report
