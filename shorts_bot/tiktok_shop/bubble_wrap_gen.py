"""Generate bubble wrap carousel slides (Gemini) + Module 1 checks for still images."""

from __future__ import annotations

import base64
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.production.images.gemini import generate_gemini_image
from shorts_bot.tiktok_shop.module1_qc import BANNED_CAPTION_PHRASES

SAMPLES_DIR = Path("data/research/course/_media/bubble_wrap/samples")
HOOK_REF = SAMPLES_DIR / "bubble wrap7.png"
CTA_REF = SAMPLES_DIR / "bubble wrap10.png"

CTA_LINES = (
    "Pause = Pop 💥\nFollow = Loud pop 🔊\nShare = Giant pop 🦖\nComment = Wild pop 🐆"
)

# Bubble wrap stills — avoid affiliate-only triggers; animals in wrap OK (course samples).
BUBBLE_WRAP_BANS = (
    "human face or human hands",
    "human appendages",
    "nude or sexual content",
    "price tag or dollar amount",
    "sale discount coupon text",
    "brand logos other than generic",
    "illegible warped gibberish text",
    "cartoon abstract unrealistic scene",
    "mirror reflection of a person",
    "supplement or beauty product boxes",
    "peptides or weight loss claims",
)


@dataclass
class BubbleSlideQC:
    passed: bool
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def summary(self) -> str:
        if self.passed:
            return "Bubble wrap slide QC PASSED"
        return "BLOCKED: " + "; ".join(self.violations[:5])


def _check_title(title: str) -> list[str]:
    lower = (title or "").lower()
    hits = []
    for phrase in BANNED_CAPTION_PHRASES:
        if phrase in lower:
            hits.append(f"Title contains banned phrase '{phrase}'")
    return hits


def qc_bubble_slide(image_path: Path, *, title: str = "", slide_role: str = "hook") -> BubbleSlideQC:
    violations = _check_title(title)
    if not image_path.is_file():
        return BubbleSlideQC(passed=False, violations=["Image file missing"])

    if not settings.has_gemini:
        return BubbleSlideQC(passed=True, warnings=["Gemini not set — skipped vision QC"])

    from shorts_bot.llm.provider import get_llm_backend

    backend = get_llm_backend()
    if backend is None or backend.provider != "gemini":
        return BubbleSlideQC(passed=True, warnings=["Vision QC skipped — no Gemini backend"])

    ban_list = "\n".join(f"- {b}" for b in BUBBLE_WRAP_BANS)
    prompt = (
        f"Bubble wrap TikTok carousel slide ({slide_role}). Check this still image.\n"
        f"List ANY of these ban triggers if visible:\n{ban_list}\n\n"
        "Also fail if: cluttered messy background, unreadable caption text, wrong format "
        "(slide 2 must NOT include hook-only title if role is cta).\n"
        "Return ONLY JSON: {\"violations\": string[], \"warnings\": string[]}"
    )
    b64 = base64.standard_b64encode(image_path.read_bytes()).decode("ascii")
    content: list[dict] = [
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
    ]
    model = (settings.gemini_vision_model or settings.gemini_model).strip()
    resp = backend.client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": content}],
        max_tokens=300,
        temperature=0.1,
    )
    raw = (resp.choices[0].message.content or "").strip()
    fence = re.search(r"\{.*\}", raw, re.S)
    data = json.loads(fence.group(0) if fence else raw)
    for v in data.get("violations") or []:
        if str(v).strip():
            violations.append(str(v).strip())
    warnings = [str(w).strip() for w in (data.get("warnings") or []) if str(w).strip()]
    return BubbleSlideQC(passed=len(violations) == 0, violations=violations, warnings=warnings)


def generate_bubble_pair(
    *,
    slug: str,
    subject: str,
    hook_text: str,
    out_dir: Path | None = None,
) -> tuple[Path, Path]:
    """Generate hook + CTA PNGs with captions baked in."""
    dest = out_dir or (settings.data_dir / "tiktok_shop" / "bubble_wrap" / slug)
    dest.mkdir(parents=True, exist_ok=True)
    hook_path = dest / "slide1_hook.png"
    cta_path = dest / "slide2_cta.png"

    hook_prompt = (
        f"Match reference style: viral TikTok bubble-wrap ASMR hook slide. "
        f"Photorealistic {subject} completely covered in tight clear bubble wrap, "
        "satisfying ASMR, vertical 9:16. Bold white text thick black outline centered: "
        f"{hook_text} "
        "Hook text ONLY — no CTA interaction lines. No humans. No prices. No watermarks."
    )
    cta_prompt = (
        f"Match reference style: viral TikTok bubble-wrap CTA slide. "
        f"Same photorealistic {subject} in clear bubble wrap, vertical 9:16, clean background like reference. "
        f"ONLY these four lines once, bold white thick black outline centered:\n{CTA_LINES}\n"
        "No hook title. No finger. No duplicate lines. No humans. No prices."
    )

    key = settings.gemini_api_key or ""
    model = settings.gemini_image_model or "gemini-3-pro-image-preview"
    refs_hook = [HOOK_REF] if HOOK_REF.is_file() else None
    refs_cta = [CTA_REF] if CTA_REF.is_file() else None

    generate_gemini_image(
        hook_prompt,
        hook_path,
        api_key=key,
        model=model,
        aspect_ratio="9:16",
        image_size=settings.gemini_image_size or "2K",
        reference_images=refs_hook,
    )
    generate_gemini_image(
        cta_prompt,
        cta_path,
        api_key=key,
        model=model,
        aspect_ratio="9:16",
        image_size=settings.gemini_image_size or "2K",
        reference_images=refs_cta,
    )
    return hook_path, cta_path
