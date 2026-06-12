"""Long-form quality gate — fails closed before upload."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from shorts_bot.production.content_format import profile_for


@dataclass
class LongQualityReport:
    pack_dir: Path
    format_id: str
    passed: bool
    total_duration_seconds: float = 0.0
    segment_count: int = 0
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def summary_lines(self) -> list[str]:
        status = "PASS" if self.passed else "FAIL"
        lines = [
            f"Long QC [{self.format_id}] — {status}",
            f"  segments: {self.segment_count} | duration: {self.total_duration_seconds:.1f}s",
        ]
        for issue in self.issues:
            lines.append(f"  [issue] {issue}")
        for warn in self.warnings:
            lines.append(f"  [warn] {warn}")
        return lines


def _load_manifest(pack_dir: Path) -> dict | None:
    path = pack_dir / "manifest.json"
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _probe_duration(path: Path) -> float:
    from shorts_bot.production.long_form_render import probe_duration

    return probe_duration(path)


def assess_long_quality(
    pack_dir: Path,
    *,
    strict_duration: bool = False,
) -> LongQualityReport:
    """Validate long pack manifest + output video."""
    manifest = _load_manifest(pack_dir)
    if not manifest:
        return LongQualityReport(
            pack_dir=pack_dir,
            format_id="unknown",
            passed=False,
            issues=["Missing or invalid manifest.json"],
        )

    format_id = str(manifest.get("format") or "long_compilation")
    prof = profile_for(format_id if format_id in ("long_compilation", "long_still", "long_hybrid") else "long_compilation")

    report = LongQualityReport(
        pack_dir=pack_dir,
        format_id=format_id,
        passed=True,
    )

    segments = manifest.get("segments") or []
    report.segment_count = len(segments)

    output_name = str(manifest.get("output_video") or "final_long.mp4")
    output_path = pack_dir / output_name
    if not output_path.is_file():
        report.issues.append(f"Missing output video: {output_name}")
    else:
        size = output_path.stat().st_size
        if size < 50_000:
            report.issues.append(f"Output video too small ({size} bytes)")
        try:
            report.total_duration_seconds = _probe_duration(output_path)
        except Exception as exc:
            report.issues.append(f"Cannot probe output duration: {exc}")

    if format_id == "long_compilation":
        if report.segment_count < 3:
            report.issues.append(
                f"Compilation needs 3–5 Shorts; found {report.segment_count}"
            )
        elif report.segment_count > 5:
            report.warnings.append(
                f"Compilation has {report.segment_count} segments (target 3–5)"
            )

        min_stitch = 60.0
        target_min, target_max = prof.target_duration_seconds
        if report.total_duration_seconds < min_stitch:
            report.issues.append(
                f"Total duration {report.total_duration_seconds:.1f}s < {min_stitch:.0f}s minimum"
            )
        elif report.total_duration_seconds < target_min:
            report.warnings.append(
                f"Duration {report.total_duration_seconds:.1f}s below {target_min / 60:.0f} min target "
                "(add bridge VO between stories for watch hours)"
            )
            if strict_duration:
                report.issues.append(
                    f"Strict mode: duration must be ≥ {target_min:.0f}s"
                )
        elif report.total_duration_seconds > target_max * 1.15:
            report.warnings.append(
                f"Duration {report.total_duration_seconds:.1f}s exceeds profile max {target_max:.0f}s"
            )

        for i, seg in enumerate(segments):
            src_name = str(seg.get("source_video") or seg.get("landscape_video") or "")
            if src_name:
                src_path = pack_dir / "landscape_segments" / src_name
                if not src_path.is_file():
                    draft_id = seg.get("draft_id")
                    if draft_id:
                        alt = pack_dir / "landscape_segments" / f"draft_{draft_id}_16x9.mp4"
                        if not alt.is_file():
                            report.warnings.append(
                                f"Segment {i}: landscape file missing ({src_name})"
                            )

    elif format_id == "long_still":
        word_target = manifest.get("word_count") or 0
        if word_target and word_target < 800:
            report.warnings.append(
                f"Script word count {word_target} below 800-word bar for long_still"
            )
        beat_count = len(manifest.get("beats") or segments)
        if beat_count < 12:
            report.warnings.append(
                f"Only {beat_count} visual beats — target 12–20 for long_still"
            )

    report.passed = not report.issues
    return report
