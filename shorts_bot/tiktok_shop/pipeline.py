"""Affiliate clip pipeline — subagent checklist, validation, prompt file helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from shorts_bot.config import settings

# CEO must dispatch these employees in order (see docs/PIPELINE_SYSTEM_DESIGN.md)
PIPELINE_SUBAGENTS: tuple[tuple[str, str, bool], ...] = (
    ("product-video-prompt-builder", "Kling video prompt from Module 4 + reference image", False),
    ("video-visual-critic", "Gemini frames + reference still — regen loop if motion/quality off", True),
    ("video-editor", "Pan loop ~10s from 5s Kling raw", True),
    ("video-caption-writer", "On-screen hook copy (no sale/price words)", False),
    ("module1-qc-runner", "Mandatory QC gate before enqueue", True),
)

REQUIRED_ASPECT = "9:16"
TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920


@dataclass
class PipelineCheck:
    ok: bool
    errors: list[str]
    warnings: list[str]


def prompts_dir() -> Path:
    return settings.data_dir / "tiktok_shop" / "prompts"


def prompt_path_for_product(product_name: str) -> Path:
    from shorts_bot.tiktok_shop.render import _slug

    return prompts_dir() / f"{_slug(product_name)}.kling.txt"


def load_prompt_file(path: Path | str) -> str:
    text = Path(path).read_text(encoding="utf-8").strip()
    if not text:
        raise RuntimeError(f"Prompt file is empty: {path}")
    return text


def save_prompt_file(*, product_name: str, prompt: str, path: Path | None = None) -> Path:
    dest = path or prompt_path_for_product(product_name)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(prompt.strip() + "\n", encoding="utf-8")
    return dest


def checklist_text(*, product: str = "", mission_id: str = "") -> str:
    lines = [
        "Affiliate clip pipeline — required subagents (CEO orchestrates)",
        "",
    ]
    if mission_id:
        lines.append(f"Mission: {mission_id}")
    if product:
        lines.append(f"Product: {product}")
    lines.append("")
    for i, (agent, desc, bg) in enumerate(PIPELINE_SUBAGENTS, 1):
        mode = "background" if bg else "foreground — attach images"
        lines.append(f"{i}. {agent} ({mode})")
        lines.append(f"   {desc}")
    lines.extend(
        [
            "",
            "Mechanical (CEO on VM):",
            "  factory_cli prompt-dispatch --product NAME --product-image PATH [--reference-image PATH]",
            "  → dispatch product-video-prompt-builder with output; save prompt to prompts/NAME.kling.txt",
            "  factory_cli render --product NAME --image PATH --prompt-file prompts/NAME.kling.txt",
            "  factory_cli visual-review (video-visual-critic) — regen if needed",
            "  factory_cli hook-lines --product NAME (video-caption-writer)",
            "  factory_cli qc --video PATH --product NAME --caption ...",
        ]
    )
    return "\n".join(lines)


def validate_before_render(
    *,
    product_name: str = "",
    product_image: Path | None = None,
    reference_image: Path | None = None,
    prompt_file: Path | None = None,
    prompt_text: str = "",
) -> PipelineCheck:
    errors: list[str] = []
    warnings: list[str] = []

    prompt = (prompt_text or "").strip()
    if prompt_file:
        pf = Path(prompt_file)
        if not pf.is_file():
            errors.append(f"Prompt file missing: {pf} — run product-video-prompt-builder first")
        else:
            prompt = load_prompt_file(pf)

    if not prompt:
        errors.append(
            "Kling prompt required — delegate to product-video-prompt-builder; "
            "save with factory_cli save-prompt or --prompt-file"
        )
    elif len(prompt) < 80:
        warnings.append("Prompt looks very short — prompt builder should output a full paragraph")

    if product_image is None or not Path(product_image).is_file():
        errors.append(f"Module 4 product image required: {product_image or '(missing)'}")
    else:
        try:
            from shorts_bot.tiktok_shop.product_images import validate_module4_image

            iv = validate_module4_image(Path(product_image).read_bytes())
            if iv.warnings:
                warnings.extend(iv.warnings)
            if iv.errors:
                errors.extend(iv.errors)
        except Exception as exc:
            warnings.append(f"Could not validate product image: {exc}")

    if reference_image and not Path(reference_image).is_file():
        warnings.append(f"Reference image path not found (optional but recommended): {reference_image}")
    elif reference_image is None and product_name:
        warnings.append("No reference image — Module 4 scale may be wrong; add --reference-image")

    return PipelineCheck(ok=not errors, errors=errors, warnings=warnings)


def dispatch_brief(
    *,
    product_name: str,
    product_image: Path,
    reference_image: Path | None = None,
    mission_id: str = "",
    visual_handoff: str = "",
) -> str:
    """Text block CEO pastes when dispatching product-video-prompt-builder."""
    lines = [
        f"Product: {product_name}",
        f"Module 4 product image (exact reference): {product_image.resolve()}",
    ]
    if reference_image and Path(reference_image).is_file():
        lines.append(f"Reference image (scale/context — use leftmost when reasoning): {Path(reference_image).resolve()}")
    else:
        lines.append("Reference image: none — infer scale from product category")
    if mission_id:
        lines.append(f"MISSION_ID={mission_id}")
    lines.extend(
        [
            "",
            "Requirements:",
            "- Output ONE Kling 2.6 video prompt paragraph only",
            "- Rich staged background (NOT plain white box — reduces still-image ban risk)",
            "- Product stationary; multi-axis arc camera with slight handheld micro-shake",
            "- Vertical 9:16 TikTok Shop framing",
            "- Module 1 compliant — zero ban triggers",
        ]
    )
    if visual_handoff.strip():
        lines.extend(["", "Visual critic handoff:", visual_handoff.strip()])
    lines.extend(
        [
            "",
            "Save prompt:",
            f"  python3 -m shorts_bot.tiktok_shop.factory_cli save-prompt --product \"{product_name}\" --prompt \"...\"",
        ]
    )
    return "\n".join(lines)
