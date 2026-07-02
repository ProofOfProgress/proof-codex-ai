"""Gemini visual feedback — pre/post render critique for prompt refinement loop."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.tiktok_shop.module1_qc import (
    _extract_frame,
    _pick_frame_times,
    _probe_duration,
    run_module1_qc,
)


@dataclass
class VisualCritiqueReport:
    """Commercial + motion quality review (separate from strict Module 1 QC gate)."""

    kind: str  # reference_image | video
    product: str
    score: float = 0.0
    good_enough: bool = False
    summary: str = ""
    issues: list[str] = field(default_factory=list)
    prompt_fixes: list[str] = field(default_factory=list)
    module1_risks: list[str] = field(default_factory=list)
    arc_camera_visible: bool | None = None
    product_fidelity: str = ""
    reference_image: str = ""
    video_path: str = ""
    prompt_used: str = ""
    frame_paths: list[str] = field(default_factory=list)
    revised_prompt: str = ""
    module1_qc_passed: bool | None = None
    checked_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def handoff_for_prompt_builder(self) -> str:
        """Plain-English block CEO pastes into product-video-prompt-builder."""
        lines = [
            f"Visual critic feedback for {self.product or 'product'} ({self.kind})",
            f"Score: {self.score}/10 — good enough: {'yes' if self.good_enough else 'no'}",
            "",
            self.summary or "(no summary)",
        ]
        if self.issues:
            lines.extend(["", "Issues seen:", *[f"- {i}" for i in self.issues]])
        if self.prompt_fixes:
            lines.extend(["", "Prompt changes needed:", *[f"- {f}" for f in self.prompt_fixes]])
        if self.module1_risks:
            lines.extend(["", "Module 1 risks:", *[f"- {r}" for r in self.module1_risks]])
        if self.prompt_used:
            lines.extend(["", "Previous Kling prompt:", self.prompt_used[:2000]])
        if self.revised_prompt:
            lines.extend(["", "Suggested revised prompt (starting point):", self.revised_prompt])
        lines.append("")
        lines.append(
            "Rewrite the Kling video prompt to fix the issues above. Module 1 compliant. Output prompt text only."
        )
        return "\n".join(lines)


def _gemini_json(*, prompt: str, image_paths: list[Path], max_tokens: int = 1500) -> dict:
    from shorts_bot.llm.gemini_utils import openai_chat_json, visual_critic_context

    ctx = visual_critic_context()
    full_prompt = f"{ctx}\n\n{prompt}" if ctx else prompt
    return openai_chat_json(prompt=full_prompt, image_paths=image_paths, max_tokens=max_tokens)


def _gemini_text(*, prompt: str, max_tokens: int = 1200) -> str:
    from shorts_bot.llm.gemini_utils import openai_chat_text, revision_model

    return openai_chat_text(prompt=prompt, model=revision_model(), max_tokens=max_tokens)


def _feedback_dir() -> Path:
    return settings.data_dir / "tiktok_shop" / "visual_feedback"


def save_report(report: VisualCritiqueReport, *, stem: str) -> Path:
    out_dir = _feedback_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{stem}.json"
    payload = report.to_dict()
    if not payload.get("checked_at"):
        payload["checked_at"] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def review_reference_image(
    image_path: Path,
    *,
    product: str = "",
) -> VisualCritiqueReport:
    """Pre-render: is the Module 4 still good for Kling + arc-camera prompt?"""
    if not image_path.is_file():
        raise FileNotFoundError(image_path)

    prompt = (
        "You are a TikTok Shop affiliate video art director reviewing a MODULE 4 product still "
        "before Kling image-to-video generation.\n\n"
        f"Product: {product[:120] or 'unknown'}\n\n"
        "Judge whether this image will produce a GOOD 5s product clip with an arc-camera prompt.\n"
        "Check: staged environment with visible depth/texture (NOT plain white listing box or gray void), "
        "9:16 full-bleed framing, product fully visible and stationary-ready, "
        "no humans/hands, no screens with UI, no phone screens or app icons, "
        "no third-party brand logos except on the advertised product, "
        "lighting suitable for believable set extension with parallax for arc-camera motion.\n\n"
        "Return ONLY JSON:\n"
        '{"score": number 1-10, "ready_for_kling": bool, "good_enough": bool, '
        '"summary": string, "issues": string[], "suggestions": string[], '
        '"prompt_fixes": string[]}\n'
        "prompt_fixes = what to tell the video prompt writer if we proceed anyway."
    )
    data = _gemini_json(prompt=prompt, image_paths=[image_path])
    fixes = [str(x) for x in (data.get("prompt_fixes") or data.get("suggestions") or []) if str(x).strip()]
    report = VisualCritiqueReport(
        kind="reference_image",
        product=product,
        score=float(data.get("score") or 0),
        good_enough=bool(data.get("good_enough", data.get("ready_for_kling", False))),
        summary=str(data.get("summary") or ""),
        issues=[str(x) for x in (data.get("issues") or []) if str(x).strip()],
        prompt_fixes=fixes,
        reference_image=str(image_path),
        checked_at=datetime.now(timezone.utc).isoformat(),
    )
    save_report(report, stem=f"image_{image_path.stem}")
    return report


def extract_video_frames(video_path: Path, *, max_frames: int | None = None) -> list[tuple[float, Path]]:
    """Sample frames from a rendered clip for Gemini review."""
    duration = _probe_duration(video_path)
    limit = max_frames or settings.vision_qc_max_frames
    times = _pick_frame_times(duration, max_frames=limit)
    out_dir = _feedback_dir() / f"frames_{video_path.stem}"
    out_dir.mkdir(parents=True, exist_ok=True)
    frames: list[tuple[float, Path]] = []
    for i, t in enumerate(times):
        path = out_dir / f"frame_{i:02d}_{t:.1f}s.jpg"
        _extract_frame(video_path, t, path)
        frames.append((t, path))
    return frames


def review_video(
    video_path: Path,
    *,
    product: str = "",
    reference_image: Path | None = None,
    prompt_used: str = "",
    include_module1_qc: bool = True,
) -> VisualCritiqueReport:
    """
    Post-render: Gemini watches video frames (+ optional reference still) and returns
    actionable feedback for the prompt builder / regen decision.
    """
    if not video_path.is_file():
        raise FileNotFoundError(video_path)

    frames = extract_video_frames(video_path, max_frames=3)
    frame_paths = [p for _, p in frames]
    labels = ", ".join(f"{t:.1f}s" for t, _ in frames)

    ref_note = ""
    image_paths = list(frame_paths)
    if reference_image and reference_image.is_file():
        image_paths = [reference_image, *frame_paths]
        ref_note = "First image = Module 4 reference still. Remaining images = video frames.\n"

    prompt = (
        "You are a TikTok Shop affiliate video quality critic helping improve Kling prompts.\n"
        f"Product: {product[:120] or 'unknown'}\n"
        f"{ref_note}"
        f"Video frames at: {labels}\n"
    )
    if prompt_used.strip():
        prompt += f"\nKling prompt used (excerpt):\n{prompt_used.strip()[:600]}\n"

    prompt += (
        "\nEvaluate COMMERCIAL readiness and MOTION quality for a 5–10s Shop affiliate clip.\n"
        "Focus on: visible arc/multi-axis camera with clear SIDE-TO-SIDE lateral travel (NOT static tripod), "
        "product stationary, background parallax or decor shifting relative to product (still-frame ban risk), "
        "product matches reference, readable branding, rich staged background with depth "
        "(NOT plain white box, gray letterbox bars, or frozen still photograph), "
        "believable lighting, no obvious AI glitches, no phone/laptop screens with UI, "
        "no third-party brand logos besides advertised product.\n"
        "Official coach 2026-06-29: TikTok flags still-frame even when some motion exists — "
        "require ~25% more noticeable lateral movement + micro-shake or moving background cues.\n\n"
        "Return ONLY JSON:\n"
        '{"score": number 1-10, "good_enough": bool, "commercial_ready": bool, '
        '"summary": string, "issues": string[], "prompt_fixes": string[], '
        '"module1_risks": string[], "arc_camera_visible": bool, '
        '"product_fidelity": "good"|"fair"|"poor"}\n'
        "good_enough=true only if you would approve one regen max before posting.\n"
        "prompt_fixes = concrete instructions for the video prompt writer (not generic advice)."
    )

    data = _gemini_json(prompt=prompt, image_paths=image_paths, max_tokens=4096)

    module1_passed: bool | None = None
    if include_module1_qc:
        qc = run_module1_qc(video_path, product=product)
        module1_passed = qc.passed
        for v in qc.violations:
            if v not in (data.get("module1_risks") or []):
                data.setdefault("module1_risks", [])
                if isinstance(data["module1_risks"], list):
                    data["module1_risks"].append(v)

    good = bool(data.get("good_enough"))
    if module1_passed is False:
        good = False

    report = VisualCritiqueReport(
        kind="video",
        product=product,
        score=float(data.get("score") or 0),
        good_enough=good,
        summary=str(data.get("summary") or ""),
        issues=[str(x) for x in (data.get("issues") or []) if str(x).strip()],
        prompt_fixes=[str(x) for x in (data.get("prompt_fixes") or []) if str(x).strip()],
        module1_risks=[str(x) for x in (data.get("module1_risks") or []) if str(x).strip()],
        arc_camera_visible=data.get("arc_camera_visible"),
        product_fidelity=str(data.get("product_fidelity") or ""),
        reference_image=str(reference_image) if reference_image else "",
        video_path=str(video_path),
        prompt_used=prompt_used,
        frame_paths=[str(p) for p in frame_paths],
        module1_qc_passed=module1_passed,
        checked_at=datetime.now(timezone.utc).isoformat(),
    )
    save_report(report, stem=f"video_{video_path.stem}")
    return report


def suggest_prompt_revision(
    *,
    original_prompt: str,
    critique: VisualCritiqueReport,
    product: str = "",
) -> str:
    """Text-only Gemini call — returns a revised Kling prompt addressing critique."""
    product = product or critique.product
    fixes = critique.prompt_fixes or critique.issues
    fix_block = "\n".join(f"- {f}" for f in fixes) or "- Improve arc camera and product fidelity"
    text_prompt = (
        "You rewrite Kling image-to-video prompts for TikTok Shop affiliate clips.\n"
        f"Product: {product[:120] or 'unknown'}\n\n"
        "Original prompt:\n"
        f"{original_prompt.strip()}\n\n"
        "Visual critic feedback:\n"
        f"{critique.summary}\n\n"
        "Required fixes:\n"
        f"{fix_block}\n\n"
        "Rules: Module 1 compliant — arc/multi-axis camera with clear lateral side-to-side travel, "
        "gentle handheld micro-shake, background parallax, product stationary, no humans/pets, "
        "no screens, no water/fire, no static camera, preserve product from uploaded image.\n"
        "Output ONLY the revised prompt paragraph — no headings or explanation."
    )
    revised = _gemini_text(prompt=text_prompt)
    revised = re.sub(r"^```.*?\n", "", revised)
    revised = re.sub(r"\n```$", "", revised.strip())
    return revised.strip()


def review_and_suggest_prompt(
    video_path: Path,
    *,
    product: str = "",
    reference_image: Path | None = None,
    prompt_used: str = "",
) -> VisualCritiqueReport:
    """Full loop step: review video → auto-suggest revised prompt if not good enough."""
    report = review_video(
        video_path,
        product=product,
        reference_image=reference_image,
        prompt_used=prompt_used,
    )
    if prompt_used.strip() and not report.good_enough:
        report.revised_prompt = suggest_prompt_revision(
            original_prompt=prompt_used,
            critique=report,
            product=product,
        )
        save_report(report, stem=f"video_{video_path.stem}")
    return report


def format_report_plain(report: VisualCritiqueReport) -> str:
    lines = [
        f"Visual feedback ({report.kind}) — {report.product or 'product'}",
        f"Score: {report.score}/10 | Good enough: {'YES' if report.good_enough else 'NO'}",
    ]
    if report.module1_qc_passed is not None:
        lines.append(f"Module 1 QC: {'PASSED' if report.module1_qc_passed else 'BLOCKED'}")
    if report.summary:
        lines.append("")
        lines.append(report.summary)
    if report.issues:
        lines.extend(["", "Issues:", *[f"  • {i}" for i in report.issues]])
    if report.prompt_fixes:
        lines.extend(["", "Prompt fixes:", *[f"  • {f}" for f in report.prompt_fixes]])
    if report.revised_prompt:
        lines.extend(["", "Suggested revised prompt:", report.revised_prompt])
    return "\n".join(lines)
