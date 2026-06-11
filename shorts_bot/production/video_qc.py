"""Post-render video quality checks — duration, silence, file health."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from shorts_bot.config import settings


@dataclass
class VideoQCReport:
    passed: bool
    duration_seconds: float
    file_size_bytes: int
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def summary(self) -> str:
        if self.passed:
            base = f"Video QC OK ({self.duration_seconds:.1f}s, {self.file_size_bytes // 1024}KB)"
            if self.warnings:
                return base + f" — warnings: {'; '.join(self.warnings[:2])}"
            return base
        return "Video QC failed: " + "; ".join(self.issues)


def _probe_duration(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        text=True,
    )
    return float(out.strip())


def _mean_volume_db(path: Path) -> float | None:
    try:
        out = subprocess.run(
            [
                "ffmpeg",
                "-i",
                str(path),
                "-af",
                "volumedetect",
                "-f",
                "null",
                "-",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        for line in (out.stderr or "").splitlines():
            if "mean_volume:" in line:
                return float(line.split("mean_volume:")[1].split("dB")[0].strip())
    except Exception:
        return None
    return None


def run_video_qc(
    video_path: Path,
    *,
    expected_min_seconds: float | None = None,
    expected_max_seconds: float | None = None,
) -> VideoQCReport:
    issues: list[str] = []
    warnings: list[str] = []

    if not video_path.exists():
        return VideoQCReport(False, 0.0, 0, issues=["video file missing"])

    size = video_path.stat().st_size
    if size < 50_000:
        issues.append(f"file too small ({size} bytes)")

    try:
        duration = _probe_duration(video_path)
    except Exception as exc:
        return VideoQCReport(False, 0.0, size, issues=[f"ffprobe failed: {exc}"])

    min_s = expected_min_seconds or settings.video_min_duration_seconds
    max_s = expected_max_seconds or settings.video_max_duration_seconds
    if duration < min_s:
        issues.append(f"duration {duration:.1f}s < min {min_s}s")
    if duration > max_s:
        warnings.append(f"duration {duration:.1f}s > recommended max {max_s}s for Shorts")

    vol = _mean_volume_db(video_path)
    if vol is not None:
        if vol < -35:
            warnings.append(f"audio quiet (mean {vol:.1f} dB)")
        if vol > -5:
            warnings.append(f"audio may clip (mean {vol:.1f} dB)")

    passed = len(issues) == 0

    return VideoQCReport(
        passed=passed,
        duration_seconds=duration,
        file_size_bytes=size,
        issues=issues,
        warnings=warnings,
    )
