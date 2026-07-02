"""Mandatory Module 1 pre-upload QC — course violation triggers must be ZERO before post."""

from __future__ import annotations

import base64
import json
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from io import BytesIO
from pathlib import Path

from shorts_bot.config import settings

# Course: module_01_read_before_anything.md — Video Don'ts (ban triggers)
MODULE1_VIDEO_VIOLATIONS: tuple[str, ...] = (
    "Moving water",
    "Moving fire",
    "Steam",
    "Dirt, sand, or powder",
    "Pulsing light",
    "Electronic screens with movement",
    "Phone screens with visible UI or app icons",
    "Recognizable third-party brands or logos besides advertised product",
    "Mobile app icons or recognizable apps in frame",
    "Mismatching lighting between product and environment",
    "Same lighting as the TikTok Shop listing image",
    "Hieroglyphic or illegible text",
    "Warped or mis-scaled product sizing",
    "Humans or human appendages",
    "Living beings — pets or animals",
    "Overly moving foliage",
    "Moving products",
    "Mis-colored products",
    "Supplement or beauty product boxes",
    "Peptides",
    "Weight loss products with claims on packaging",
    "Cluttered environments",
    "Product not in frame 80%+ of video",
    "Product not entirely in frame during image generation",
    "Unrealistic environments (cartoon, spaceship, abstract)",
    "Static camera movement",
    "Exaggerated human bobbing or movement",
    "Camera movement in only 1 axis",
    "Same environment as the listing image",
    "Other brand titles in frame",
    "Prices or retail messaging in background",
    "Mirrors or human reflections",
    "Levitating products",
    "Physics-breaking product orientation",
)

BANNED_CAPTION_PHRASES: tuple[str, ...] = (
    "triple discount",
    "double discount",
    "flash sale",
    "coupon glitch",
    "violently discounted",
    "on sale",
    "percent off",
    "% off",
    "limited time",
    "running low",
    "last chance",
    "won't stay this cheap",
    "basically a steal",
    "at this price",
)

# Module 7 — misinformation words (June 2026 course baseline + GROUP_CALLS)
MODULE7_BANNED_CAPTION_WORDS: tuple[str, ...] = (
    "sale",
    "price",
    "discount",
    "coupon",
    "free shipping",
    "clearance",
    "bogo",
)


@dataclass
class Module1QCReport:
    passed: bool
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    frame_paths: list[str] = field(default_factory=list)
    vision_ran: bool = False

    def summary(self) -> str:
        if self.passed:
            base = "Module 1 QC PASSED — zero ban triggers"
            if self.warnings:
                return base + f" (warnings: {'; '.join(self.warnings[:2])})"
            return base
        return "Module 1 QC BLOCKED: " + "; ".join(self.violations[:5])


def qc_report_path(video_path: Path) -> Path:
    return settings.data_dir / "tiktok_shop" / "module1_qc" / f"{video_path.stem}.json"


def load_qc_report(video_path: Path) -> dict | None:
    path = qc_report_path(video_path)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def qc_report_stale_for_video(video_path: Path, report: dict) -> bool:
    """True when the MP4 changed after the saved QC report."""
    if not video_path.is_file():
        return True
    checked = str(report.get("checked_at") or "")
    if not checked:
        return True
    try:
        checked_dt = datetime.fromisoformat(checked.replace("Z", "+00:00"))
        if checked_dt.tzinfo is None:
            checked_dt = checked_dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return True
    return video_path.stat().st_mtime > checked_dt.timestamp() + 1.0


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


def _extract_frame(video_path: Path, t: float, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    width = settings.vision_qc_frame_width
    quality = settings.vision_qc_jpeg_quality
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
            f"scale={width}:-2",
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


def _pick_frame_times(duration: float, *, max_frames: int) -> list[float]:
    if duration <= 0:
        return [0.3]
    candidates = [0.5, duration * 0.25, duration * 0.5, duration * 0.75, max(0.3, duration - 0.6)]
    picked: list[float] = []
    for t in sorted(candidates):
        t = min(max(0.3, t), max(0.3, duration - 0.3))
        if not picked or abs(t - picked[-1]) >= 0.8:
            picked.append(round(t, 2))
        if len(picked) >= max_frames:
            break
    return picked[:max_frames]


def _probe_dimensions(video_path: Path) -> tuple[int, int]:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height",
            "-of",
            "csv=p=0:s=x",
            str(video_path),
        ],
        text=True,
    ).strip()
    if "x" not in out:
        raise ValueError(f"Could not read video dimensions: {out!r}")
    w_s, h_s = out.split("x", 1)
    return int(w_s), int(h_s)


def _check_aspect_ratio(width: int, height: int) -> list[str]:
    if width <= 0 or height <= 0:
        return ["Video dimensions invalid (width/height must be positive)"]
    ratio = width / height
    target = settings.module1_target_aspect_ratio
    tol = settings.module1_aspect_ratio_tolerance
    if abs(ratio - target) > tol:
        return [
            f"Video aspect ratio {width}x{height} ({ratio:.3f}) is not 9:16 "
            f"(expected ~{target:.3f}) — letterbox/border risk"
        ]
    return []


def _check_caption(caption: str) -> list[str]:
    lower = (caption or "").lower()
    hits: list[str] = []
    for phrase in BANNED_CAPTION_PHRASES:
        if phrase in lower:
            hits.append(f"Module 7 / posting don't: caption contains banned phrase '{phrase}'")
    for word in MODULE7_BANNED_CAPTION_WORDS:
        if re.search(rf"\b{re.escape(word)}\b", lower):
            hits.append(f"Module 7 misinformation: caption contains banned word '{word}'")
    return hits


def _post_log_rows() -> list[dict]:
    path = settings.data_dir / "tiktok_shop" / "post_log.jsonl"
    if not path.is_file():
        return []
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def _check_posting_rules(
    *,
    account_id: str,
    product: str,
) -> list[str]:
    """Module 1 posting don'ts — spacing, duplicate product, daily max."""
    violations: list[str] = []
    now = datetime.now(timezone.utc)
    today = now.date().isoformat()
    ok_today = [
        r
        for r in _post_log_rows()
        if r.get("ok") and str(r.get("at", "")).startswith(today) and r.get("account_id") == account_id
    ]
    if len(ok_today) >= 30:
        violations.append("Posting Don't: more than 30 posts today on this account")

    product_key = (product or "").strip().lower()
    if product_key:
        for row in ok_today:
            if str(row.get("product") or "").strip().lower() == product_key:
                violations.append(f"Posting Don't: same product already posted today ({product})")
                break

    recent = [
        r
        for r in _post_log_rows()
        if r.get("ok") and r.get("account_id") == account_id
    ]
    if recent:
        last_at = recent[-1].get("at")
        try:
            last_dt = datetime.fromisoformat(str(last_at).replace("Z", "+00:00"))
            if last_dt.tzinfo is None:
                last_dt = last_dt.replace(tzinfo=timezone.utc)
            gap = now - last_dt
            min_gap = timedelta(minutes=settings.module1_min_post_interval_minutes)
            if gap < min_gap:
                mins = int(min_gap.total_seconds() // 60)
                violations.append(f"Posting Don't: last post was {int(gap.total_seconds() // 60)}m ago (min {mins}m)")
        except (TypeError, ValueError):
            pass
    return violations


def _parse_vision_json(raw: str) -> dict:
    text = raw.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    if fence:
        text = fence.group(1)
    else:
        brace = re.search(r"\{.*\}", text, re.S)
        if brace:
            text = brace.group(0)
    return json.loads(text)


def _gemini_check_frames(
    frames: list[tuple[float, Path]],
    *,
    product: str,
) -> tuple[list[str], list[str]]:
    from shorts_bot.llm.provider import get_llm_backend

    from shorts_bot.llm.gemini_utils import call_with_retry, vision_model

    backend = get_llm_backend()
    if backend is None or backend.provider != "gemini":
        raise RuntimeError("GEMINI_API_KEY required for Module 1 vision QC (mandatory before upload)")

    model = vision_model()
    labels = ", ".join(f"{t:.1f}s" for t, _ in frames)
    violation_list = "\n".join(f"- {v}" for v in MODULE1_VIDEO_VIOLATIONS)
    prompt = (
        "You are TikTok Shop Module 1 compliance QC. Product: "
        f"{product[:120] or 'unknown'}. Frames at: {labels}.\n\n"
        "Check ONLY for these ban triggers (course Module 1). If ANY appear in ANY frame, "
        "list them in violations. Zero tolerance.\n\n"
        f"{violation_list}\n\n"
        "Owner override (2026-06-28): ONLY the advertised product's brand may be visible. "
        "Flag any phone/laptop/tablet screen showing UI, app icons, or home screen. "
        "Flag Apple, MacBook, Instagram, Facebook, or any third-party logo not on the product itself.\n\n"
        "Official coach (2026-06-29): TikTok still-frame violations happen even when some motion "
        "exists — flag if the clip looks like a photograph, lacks clear side-to-side parallax, "
        "or background objects do not shift relative to the product.\n\n"
        "Also verify Video Do's where visible: arc camera with noticeable lateral travel (not static), "
        "product ~80%+ in frame, legible text if any, matching lighting, non-cluttered environment "
        "with depth for parallax.\n\n"
        "Return ONLY JSON: "
        '{"violations": string[], "warnings": string[], "product_in_frame_80pct": bool, '
        '"arc_camera": bool}'
    )

    content: list[dict] = [{"type": "text", "text": prompt}]
    for _t, path in frames:
        b64 = base64.standard_b64encode(path.read_bytes()).decode("ascii")
        content.append(
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
        )

    def _call():
        resp = backend.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": content}],
            max_tokens=400,
            temperature=0.1,
        )
        raw = (resp.choices[0].message.content or "").strip()
        return _parse_vision_json(raw)

    data = call_with_retry(_call, label=f"module1-qc:{model}")
    violations = [str(v).strip() for v in (data.get("violations") or []) if str(v).strip()]
    warnings = [str(w).strip() for w in (data.get("warnings") or []) if str(w).strip()]
    if data.get("product_in_frame_80pct") is False:
        violations.append("Product not in frame 80%+ of video")
    if data.get("arc_camera") is False:
        violations.append("Static camera movement (need arc camera around product)")
    return violations, warnings


def _check_inter_frame_motion(frames: list[tuple[float, Path]]) -> list[str]:
    """Pixel-diff motion gate — catches still-frame risk Gemini may miss."""
    if not settings.module1_still_frame_motion_block:
        return []
    if len(frames) < 2:
        return []
    from shorts_bot.tiktok_shop.video_variants import mean_inter_frame_motion

    score = mean_inter_frame_motion([p for _, p in frames])
    if score < settings.module1_min_inter_frame_motion:
        return [
            f"Still-frame risk: insufficient motion between frames (score {score:.4f} "
            f"< {settings.module1_min_inter_frame_motion}) — add lateral parallax + micro-shake"
        ]
    return []


def run_module1_qc(
    video_path: Path,
    *,
    caption: str = "",
    product: str = "",
    account_id: str = "",
) -> Module1QCReport:
    """
    Mandatory pre-upload gate. passed=True only when violations list is empty.
    """
    violations: list[str] = []
    warnings: list[str] = []

    if not settings.module1_qc_enabled:
        warnings.append("Module 1 QC disabled in config — owner override only")
        return Module1QCReport(passed=True, warnings=warnings)

    if not video_path.exists():
        return Module1QCReport(passed=False, violations=["Video file missing"])

    violations.extend(_check_caption(caption))
    if account_id:
        violations.extend(_check_posting_rules(account_id=account_id, product=product))

    try:
        duration = _probe_duration(video_path)
    except Exception as exc:
        return Module1QCReport(passed=False, violations=[f"Could not read video duration: {exc}"])

    min_s = settings.module1_min_video_seconds
    if duration < min_s:
        violations.append(f"Posting Don't: video {duration:.1f}s (minimum {min_s}s)")

    try:
        width, height = _probe_dimensions(video_path)
        violations.extend(_check_aspect_ratio(width, height))
    except Exception as exc:
        violations.append(f"Could not verify 9:16 aspect ratio: {exc}")

    times = _pick_frame_times(duration, max_frames=settings.vision_qc_max_frames)
    qc_dir = settings.data_dir / "tiktok_shop" / "module1_qc" / video_path.stem
    frames: list[tuple[float, Path]] = []
    for i, t in enumerate(times):
        path = qc_dir / f"frame_{i:02d}_{t:.1f}s.jpg"
        try:
            _extract_frame(video_path, t, path)
        except subprocess.CalledProcessError:
            fallback = max(0.3, min(t - 0.5, duration - 0.5))
            _extract_frame(video_path, fallback, path)
            t = fallback
        frames.append((t, path))

    violations.extend(_check_inter_frame_motion(frames))

    vision_ran = False
    if settings.has_gemini:
        try:
            vis_v, vis_w = _gemini_check_frames(frames, product=product)
            violations.extend(vis_v)
            warnings.extend(vis_w)
            vision_ran = True
        except Exception as exc:
            if settings.module1_qc_blocks_upload:
                violations.append(f"Module 1 vision QC failed: {exc}")
            else:
                warnings.append(f"Vision QC skipped: {exc}")
    elif settings.module1_qc_blocks_upload:
        violations.append(
            "GEMINI_API_KEY missing — cannot run mandatory Module 1 vision QC before upload"
        )

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique_violations: list[str] = []
    for v in violations:
        key = v.lower()
        if key not in seen:
            seen.add(key)
            unique_violations.append(v)

    passed = len(unique_violations) == 0
    report = Module1QCReport(
        passed=passed,
        violations=unique_violations,
        warnings=warnings,
        duration_seconds=duration,
        frame_paths=[str(p) for _, p in frames],
        vision_ran=vision_ran,
    )
    _save_report(video_path, report)
    return report


@dataclass
class Module1QCBatchResult:
    total: int
    passed: int
    failed: int
    reports: list[tuple[Path, Module1QCReport]]


def run_module1_qc_batch(
    items: list[tuple[Path, str, str]],
    *,
    account_id: str = "",
) -> Module1QCBatchResult:
    """Run Module 1 QC on every clip — use before launch batch enqueue."""
    reports: list[tuple[Path, Module1QCReport]] = []
    passed = 0
    for video_path, caption, product in items:
        report = run_module1_qc(
            video_path,
            caption=caption,
            product=product,
            account_id=account_id,
        )
        reports.append((video_path, report))
        if report.passed:
            passed += 1
    total = len(items)
    return Module1QCBatchResult(
        total=total,
        passed=passed,
        failed=total - passed,
        reports=reports,
    )


def _save_report(video_path: Path, report: Module1QCReport) -> None:
    out = qc_report_path(video_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "video": str(video_path),
        "passed": report.passed,
        "violations": report.violations,
        "warnings": report.warnings,
        "duration_seconds": report.duration_seconds,
        "frame_paths": report.frame_paths,
        "vision_ran": report.vision_ran,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def enforce_module1_before_upload(
    video_path: Path,
    *,
    caption: str = "",
    product: str = "",
    account_id: str = "",
) -> Module1QCReport:
    """Run Module 1 QC; raises nothing — caller must block upload if not passed."""
    report = run_module1_qc(
        video_path,
        caption=caption,
        product=product,
        account_id=account_id,
    )
    return report
