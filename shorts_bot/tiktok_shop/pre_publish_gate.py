"""Unified pre-publish gate — cheap code checks first, vision only when tier allows."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from shorts_bot.config import settings
from shorts_bot.operating.tips import code_tips_for, OperatingTip
from shorts_bot.tiktok_shop.module1_qc import (
    _check_caption,
    _check_posting_rules,
    run_module1_qc,
)

Tier = Literal["fast", "standard", "full"]
ContentType = Literal["video", "carousel", "affiliate"]


@dataclass
class PrePublishReport:
    passed: bool
    tier: str
    content_type: str
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    vision_ran: bool = False
    tips_checked: list[str] = field(default_factory=list)

    def summary(self) -> str:
        if self.passed:
            base = f"Pre-publish PASSED ({self.tier}, {self.content_type})"
            if self.warnings:
                return base + f" — warnings: {'; '.join(self.warnings[:2])}"
            return base
        return "Pre-publish BLOCKED: " + "; ".join(self.violations[:5])


def _check_aigc_configured() -> list[str]:
    if not settings.zernio_declare_aigc and not settings.tiktok_declare_aigc:
        return ["T002: AI disclosure disabled in config (ZERNIO_DECLARE_AIGC / tiktok_declare_aigc)"]
    return []


def _check_carousel_two_slides(slide1: Path | None, slide2: Path | None) -> list[str]:
    violations: list[str] = []
    if not slide1 or not slide2:
        return ["T004: carousel requires slide1 + slide2 PNG paths"]
    for label, p in (("slide1", slide1), ("slide2", slide2)):
        if not p.is_file():
            violations.append(f"T004: {label} missing: {p}")
        elif p.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp"):
            violations.append(f"T004: {label} must be image PNG/JPEG, not {p.suffix}")
    return violations


def _run_code_check(
    check: str,
    *,
    content_type: ContentType,
    video_path: Path | None,
    slide1: Path | None,
    slide2: Path | None,
    caption: str,
    title: str,
    product: str,
    account_id: str,
    tier: Tier,
) -> tuple[list[str], list[str], bool]:
    """Return (violations, warnings, vision_ran)."""
    violations: list[str] = []
    warnings: list[str] = []
    vision_ran = False

    if check == "aigc_configured":
        violations.extend(_check_aigc_configured())
    elif check == "caption_bans":
        text = f"{caption} {title}".strip()
        for v in _check_caption(text):
            violations.append(v.replace("Posting Don't:", "T006:"))
    elif check == "posting_rules":
        if account_id:
            violations.extend(_check_posting_rules(account_id=account_id, product=product))
    elif check == "carousel_two_slides":
        violations.extend(_check_carousel_two_slides(slide1, slide2))
    elif check == "bubble_slides":
        if tier == "fast" or not settings.module1_vision_qc_enabled:
            warnings.append("T005: bubble slide vision QC skipped (fast tier or vision disabled)")
            return violations, warnings, vision_ran
        from shorts_bot.tiktok_shop.bubble_wrap_gen import qc_bubble_slide

        for path, role in ((slide1, "hook"), (slide2, "cta")):
            if not path or not path.is_file():
                continue
            report = qc_bubble_slide(path, title=title, slide_role=role)
            if not report.passed:
                violations.append(f"T005: {path.name} — {report.summary()}")
            vision_ran = vision_ran or bool(report.warnings and "skipped" not in report.summary().lower())
    elif check == "module1_video":
        if content_type != "video" or not video_path:
            return violations, warnings, vision_ran
        if tier == "fast" or not settings.module1_vision_qc_enabled:
            violations.extend(_check_caption(caption))
            if account_id:
                violations.extend(_check_posting_rules(account_id=account_id, product=product))
            if video_path.is_file():
                from shorts_bot.tiktok_shop.module1_qc import _probe_duration

                try:
                    dur = _probe_duration(video_path)
                    if dur < settings.module1_min_video_seconds:
                        violations.append(
                            f"T003: video {dur:.1f}s (min {settings.module1_min_video_seconds}s)"
                        )
                except Exception as exc:
                    violations.append(f"T003: could not read video: {exc}")
            warnings.append("T003: Module 1 vision QC skipped (fast tier)")
            return violations, warnings, vision_ran
        qc = run_module1_qc(
            video_path,
            caption=caption,
            product=product,
            account_id=account_id,
        )
        if not qc.passed:
            violations.extend(qc.violations)
        warnings.extend(qc.warnings)
        vision_ran = qc.vision_ran
    return violations, warnings, vision_ran


def run_pre_publish_gate(
    content_type: ContentType,
    *,
    tier: Tier | None = None,
    video_path: Path | None = None,
    slide1: Path | None = None,
    slide2: Path | None = None,
    caption: str = "",
    title: str = "",
    product: str = "",
    account_id: str = "",
) -> PrePublishReport:
    """
    Required gate before Zernio/TikTok upload.

    Tiers (compute cost):
    - fast: regex + posting rules + file checks — no Gemini vision
    - standard: fast + vision when module1_vision_qc_enabled
    - full: same as standard today (alias for module1 video path)
    """
    effective_tier: Tier = tier or settings.pre_publish_default_tier
    if effective_tier not in ("fast", "standard", "full"):
        effective_tier = "standard"

    violations: list[str] = []
    warnings: list[str] = []
    vision_ran = False
    tips_checked: list[str] = []

    tips = code_tips_for(content_type)
    seen_checks: set[str] = set()
    for tip in tips:
        tips_checked.append(tip.id)
        check = tip.code_check or ""
        if not check or check in seen_checks:
            continue
        seen_checks.add(check)
        v, w, vr = _run_code_check(
            check,
            content_type=content_type,
            video_path=video_path,
            slide1=slide1,
            slide2=slide2,
            caption=caption,
            title=title,
            product=product,
            account_id=account_id,
            tier=effective_tier,
        )
        violations.extend(v)
        warnings.extend(w)
        vision_ran = vision_ran or vr

    if effective_tier in ("standard", "full") and not settings.module1_vision_qc_enabled:
        warnings.append("Vision QC disabled (MODULE1_VISION_QC_ENABLED=false)")

    # Deduplicate violations
    seen: set[str] = set()
    unique_v: list[str] = []
    for v in violations:
        key = v.lower()
        if key not in seen:
            seen.add(key)
            unique_v.append(v)

    passed = len(unique_v) == 0
    if not settings.pre_publish_blocks_upload and unique_v:
        warnings.append("Pre-publish violations present but PRE_PUBLISH_BLOCKS_UPLOAD=false")

    return PrePublishReport(
        passed=passed,
        tier=effective_tier,
        content_type=content_type,
        violations=unique_v,
        warnings=warnings,
        vision_ran=vision_ran,
        tips_checked=tips_checked,
    )


def enforce_before_upload(report: PrePublishReport) -> None:
    if not report.passed and settings.pre_publish_blocks_upload:
        raise RuntimeError(report.summary())
