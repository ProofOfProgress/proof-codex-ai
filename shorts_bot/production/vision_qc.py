"""Gemini vision QC — sparse frame samples, one batched call, minimal tokens."""

from __future__ import annotations

import base64
import hashlib
import json
import re
import subprocess
from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path
from typing import Any

from shorts_bot.config import settings


@dataclass
class VisionQCReport:
    passed: bool
    score: float
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    frame_times: list[float] = field(default_factory=list)
    frame_paths: list[str] = field(default_factory=list)
    skipped_gemini: bool = False
    checks: dict[str, bool] = field(default_factory=dict)

    def summary(self) -> str:
        if self.skipped_gemini:
            return f"Vision QC skipped (no Gemini): score {self.score:.1f}/10"
        status = "OK" if self.passed else "FAILED"
        base = f"Vision QC {status} ({self.score:.1f}/10, {len(self.frame_paths)} frames)"
        if self.issues:
            return base + " — " + "; ".join(self.issues[:3])
        if self.warnings:
            return base + f" — warnings: {'; '.join(self.warnings[:2])}"
        return base


def _report_path(pack_dir: Path) -> Path:
    return pack_dir / "vision_qc.json"


def load_cached_report(pack_dir: Path, video_path: Path) -> VisionQCReport | None:
    path = _report_path(pack_dir)
    if not path.exists() or not video_path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if float(data.get("video_mtime", 0)) != video_path.stat().st_mtime:
            return None
        return VisionQCReport(
            passed=bool(data.get("passed")),
            score=float(data.get("score", 0)),
            issues=list(data.get("issues") or []),
            warnings=list(data.get("warnings") or []),
            frame_times=[float(t) for t in data.get("frame_times") or []],
            frame_paths=list(data.get("frame_paths") or []),
            skipped_gemini=bool(data.get("skipped_gemini")),
            checks=dict(data.get("checks") or {}),
        )
    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        return None


def _save_report(pack_dir: Path, video_path: Path, report: VisionQCReport) -> None:
    payload = {
        "passed": report.passed,
        "score": report.score,
        "issues": report.issues,
        "warnings": report.warnings,
        "frame_times": report.frame_times,
        "frame_paths": report.frame_paths,
        "skipped_gemini": report.skipped_gemini,
        "checks": report.checks,
        "video_mtime": video_path.stat().st_mtime,
    }
    _report_path(pack_dir).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _probe_duration(video_path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(video_path),
        ],
        text=True,
    )
    return float(out.strip())


def _load_segment_starts(pack_dir: Path) -> list[float]:
    manifest = pack_dir / "manifest.json"
    if not manifest.exists():
        return []
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
        return sorted(
            float(s.get("start_seconds", 0))
            for s in (data.get("segments") or [])
            if s.get("start_seconds") is not None
        )
    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        return []


def pick_frame_times(duration: float, pack_dir: Path, *, max_frames: int) -> list[float]:
    """Beat-aware sparse samples — hook, segment cuts, mid, pre-end."""
    starts = _load_segment_starts(pack_dir)
    candidates: list[float] = [0.8]
    if starts:
        if len(starts) >= 3:
            candidates.append(starts[len(starts) // 3])
            candidates.append(starts[(2 * len(starts)) // 3])
        elif len(starts) >= 2:
            candidates.append(starts[1])
        elif starts[0] >= 1.5:
            candidates.append(starts[0])
    candidates.extend([max(1.0, duration * 0.5), max(2.0, duration - 1.5)])

    picked: list[float] = []
    for t in sorted(candidates):
        t = min(max(0.3, t), max(0.3, duration - 0.2))
        if not picked or abs(t - picked[-1]) >= 1.2:
            picked.append(round(t, 2))
        if len(picked) >= max_frames:
            break
    return picked[:max_frames]


def _extract_frame(video_path: Path, t: float, out_path: Path, *, width: int, quality: int) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    vf = f"scale={width}:-2"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-ss",
            f"{t:.3f}",
            "-i",
            str(video_path),
            "-frames:v",
            "1",
            "-vf",
            vf,
            "-q:v",
            str(max(2, min(31, int((100 - quality) / 3)))),
            str(out_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    try:
        from PIL import Image

        img = Image.open(out_path)
        if img.mode != "RGB":
            img = img.convert("RGB")
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=quality, optimize=True)
        out_path.write_bytes(buf.getvalue())
    except Exception:
        pass


def _file_sig(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.md5(data[:4096]).hexdigest()


def _local_frame_checks(frame_paths: list[Path]) -> tuple[list[str], list[str], bool]:
    """Free checks before Gemini — black/stuck frames."""
    issues: list[str] = []
    warnings: list[str] = []
    if not frame_paths:
        issues.append("no frames extracted")
        return issues, warnings, False

    sizes = [p.stat().st_size for p in frame_paths if p.exists()]
    if not sizes or min(sizes) < 800:
        issues.append("frame extract failed or blank")
        return issues, warnings, False

    sigs = [_file_sig(p) for p in frame_paths if p.exists()]
    if len(sigs) >= 3 and len(set(sigs)) == 1:
        issues.append("video appears frozen (identical frames)")
        return issues, warnings, False

    try:
        from PIL import Image

        for p in frame_paths:
            img = Image.open(p).convert("L")
            pixels = list(img.getdata())
            if pixels:
                avg = sum(pixels) / len(pixels)
                if avg < 3:
                    issues.append(f"near-black frame at {p.name}")
                    break
                if avg < 12:
                    warnings.append(f"dark frame at {p.name} (OK for horror if scene is intentional)")
    except Exception:
        warnings.append("could not run brightness check")

    return issues, warnings, len(issues) == 0


def _parse_vision_json(raw: str) -> dict[str, Any]:
    text = raw.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    if fence:
        text = fence.group(1)
    else:
        brace = re.search(r"\{.*\}", text, re.S)
        if brace:
            text = brace.group(0)
    return json.loads(text)


def _gemini_vision_review(
    frames: list[tuple[float, Path]],
    *,
    topic: str,
    hook: str,
) -> dict[str, Any]:
    from shorts_bot.llm.provider import get_llm_backend

    backend = get_llm_backend()
    if backend is None or backend.provider != "gemini":
        raise RuntimeError("Gemini API key required for vision QC")

    model = (settings.gemini_vision_model or settings.gemini_model).strip()
    labels = ", ".join(f"{t:.1f}s" for t, _ in frames)
    prompt = (
        "QC this Don't Blink horror YouTube Short (AI motion clips + burned captions). "
        f"Frames in order at: {labels}. Topic: {topic[:80]}. Hook: {hook[:100]}.\n"
        "Return ONLY JSON keys: score (1-10), pass (bool), issues (string[]), warnings (string[]), "
        "hook_clear, captions_safe, horror_visible, no_cosy_aesthetic, scare_potential (bools). "
        "Fail pass=false if captions sit in bottom 25%, scene looks cosy/warm/self-help, stick figures, "
        "bright daylight cheer, hook frame lacks dread, or final-frame scare potential is weak."
    )

    content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
    for _t, path in frames:
        b64 = base64.standard_b64encode(path.read_bytes()).decode("ascii")
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
            }
        )

    resp = backend.client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": content}],
        max_tokens=280,
        temperature=0.2,
    )
    raw = (resp.choices[0].message.content or "").strip()
    return _parse_vision_json(raw)


def run_vision_qc(
    video_path: Path,
    pack_dir: Path,
    *,
    topic: str,
    hook: str,
    use_cache: bool = True,
) -> VisionQCReport:
    """
    Sparse frame extract + optional single Gemini vision call.
    Local checks run first to avoid tokens on obvious failures.
    """
    if not settings.vision_qc_enabled:
        return VisionQCReport(passed=True, score=10.0, skipped_gemini=True)

    if not video_path.exists():
        return VisionQCReport(passed=False, score=0.0, issues=["video missing"])

    if use_cache:
        cached = load_cached_report(pack_dir, video_path)
        if cached:
            return cached

    duration = _probe_duration(video_path)
    times = pick_frame_times(
        duration,
        pack_dir,
        max_frames=settings.vision_qc_max_frames,
    )
    frames_dir = pack_dir / "qc_frames"
    frames: list[tuple[float, Path]] = []
    for i, t in enumerate(times):
        path = frames_dir / f"qc_{i:02d}_{t:.1f}s.jpg"
        _extract_frame(
            video_path,
            t,
            path,
            width=settings.vision_qc_frame_width,
            quality=settings.vision_qc_jpeg_quality,
        )
        frames.append((t, path))

    local_issues, local_warnings, local_ok = _local_frame_checks([p for _, p in frames])
    if not local_ok:
        report = VisionQCReport(
            passed=False,
            score=0.0,
            issues=local_issues,
            warnings=local_warnings,
            frame_times=times,
            frame_paths=[str(p) for _, p in frames],
            skipped_gemini=True,
        )
        _save_report(pack_dir, video_path, report)
        return report

    issues = list(local_issues)
    warnings = list(local_warnings)
    checks: dict[str, bool] = {}
    score = 7.0
    passed = True
    skipped = False

    if settings.has_gemini:
        try:
            data = _gemini_vision_review(frames, topic=topic, hook=hook)
            score = float(data.get("score", 0))
            passed = bool(data.get("pass", score >= settings.vision_qc_min_score))
            issues.extend(str(x) for x in (data.get("issues") or []) if x)
            warnings.extend(str(x) for x in (data.get("warnings") or []) if x)
            for key in ("hook_clear", "captions_safe", "horror_visible", "no_cosy_aesthetic", "scare_potential"):
                if key in data:
                    checks[key] = bool(data[key])
            if score < settings.vision_qc_min_score:
                passed = False
                if not issues:
                    issues.append(f"vision score {score:.1f} below min {settings.vision_qc_min_score}")
        except Exception as exc:
            if settings.vision_qc_blocks_upload:
                passed = False
                issues.append(f"Gemini vision QC failed: {exc}")
            else:
                skipped = True
                warnings.append(f"Gemini vision skipped: {exc}")
                passed = True
                score = 7.0
    else:
        skipped = True
        warnings.append("GEMINI_API_KEY missing — vision QC not run")
        if settings.vision_qc_blocks_upload:
            passed = False
            issues.append("Gemini required for vision QC")
        else:
            passed = True

    report = VisionQCReport(
        passed=passed,
        score=score,
        issues=issues,
        warnings=warnings,
        frame_times=times,
        frame_paths=[str(p) for _, p in frames],
        skipped_gemini=skipped,
        checks=checks,
    )
    _save_report(pack_dir, video_path, report)
    return report
