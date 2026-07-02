"""Gemini helpers — model routing, retries, course context for vision tasks."""

from __future__ import annotations

import time
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

from shorts_bot.config import settings

# Cost-aware defaults (Jul 2026): lite for bulk OCR/scrape; flash for QC + visual critic.
DEFAULT_CHEAP_MODEL = "gemini-2.5-flash-lite"
DEFAULT_VISION_MODEL = "gemini-2.5-flash"
DEFAULT_IMAGE_MODEL = "gemini-2.5-flash-image"
DEFAULT_REVISION_MODEL = "gemini-2.5-flash-lite"

_RETRYABLE_MARKERS = ("503", "429", "overloaded", "unavailable", "deadline", "timeout")


def cheap_model() -> str:
    """Table scrape, Discord OCR, bulk text — keep on flash-lite."""
    return (settings.gemini_model or DEFAULT_CHEAP_MODEL).strip()


def vision_model() -> str:
    """Module 1 QC, visual critic, pre-render image review — flash tier."""
    raw = (settings.gemini_vision_model or "").strip()
    return raw or DEFAULT_VISION_MODEL


def image_model() -> str:
    """Module 4 sample stills."""
    return (settings.gemini_image_model or DEFAULT_IMAGE_MODEL).strip()


def revision_model() -> str:
    """Text-only prompt rewrites — lite is enough."""
    raw = (getattr(settings, "gemini_revision_model", None) or "").strip()
    if raw:
        return raw
    return cheap_model()


def _is_retryable(exc: BaseException) -> bool:
    msg = str(exc).lower()
    return any(m in msg for m in _RETRYABLE_MARKERS)


T = TypeVar("T")


def call_with_retry(
    fn: Callable[[], T],
    *,
    max_attempts: int = 4,
    base_delay_s: float = 4.0,
    label: str = "gemini",
) -> T:
    """Retry transient Gemini overload (503/429) with exponential backoff."""
    last: BaseException | None = None
    for attempt in range(max_attempts):
        try:
            return fn()
        except Exception as exc:
            last = exc
            if not _is_retryable(exc) or attempt >= max_attempts - 1:
                raise
            delay = base_delay_s * (attempt + 1)
            print(f"WARN {label} attempt {attempt + 1}/{max_attempts}: {exc} — retry in {delay:.0f}s", flush=True)
            time.sleep(delay)
    raise last  # pragma: no cover


def visual_critic_context(*, max_chars: int = 900, include_owner_file: bool = False) -> str:
    """Coach rules injected into Gemini visual critic prompts (not full fine-tune)."""
    parts: list[str] = [
        "TikTok Shop affiliate clip standards (Momentum Academy / owner overrides):",
        "- Product stays physically fixed; ONLY the camera moves (arc + lateral side-to-side).",
        "- Coach 2026-06-29: ~25% more lateral travel + handheld micro-shake; background parallax required.",
        "- Staged environment with depth — NOT plain white listing box, gray void, or letterbox bars.",
        "- No humans, pets, phone/laptop screens with UI, third-party logos except on the product.",
        "- No water, steam, fire, sale/price text. Vertical 9:16 full bleed.",
        "- Still-frame ban: flag static tripod, frozen photograph, or product rotation/spin.",
    ]
    if include_owner_file:
        prompt_builder = settings.data_dir / "research" / "course" / "PROMPT_BUILDER.md"
        if prompt_builder.is_file():
            try:
                excerpt = prompt_builder.read_text(encoding="utf-8")[: max_chars // 2]
                if excerpt.strip():
                    parts.extend(["", "Owner PROMPT_BUILDER excerpt:", excerpt.strip()])
            except OSError:
                pass
    return "\n".join(parts)[:max_chars]


def openai_chat_json(
    *,
    prompt: str,
    image_paths: list[Path],
    model: str | None = None,
    max_tokens: int = 1500,
    temperature: float = 0.2,
) -> dict[str, Any]:
    """Vision JSON call via OpenAI-compatible Gemini endpoint."""
    import base64

    from shorts_bot.llm.provider import get_llm_backend
    from shorts_bot.tiktok_shop.module1_qc import _parse_vision_json

    backend = get_llm_backend()
    if backend is None or backend.provider != "gemini":
        raise RuntimeError("GEMINI_API_KEY required — add in Cursor Secrets")

    use_model = (model or vision_model()).strip()
    content: list[dict] = [{"type": "text", "text": prompt}]
    for path in image_paths:
        if not path.is_file():
            continue
        b64 = base64.standard_b64encode(path.read_bytes()).decode("ascii")
        content.append(
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
        )

    def _call():
        resp = backend.client.chat.completions.create(
            model=use_model,
            messages=[{"role": "user", "content": content}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        raw = (resp.choices[0].message.content or "").strip()
        if not raw:
            raise RuntimeError("503 empty Gemini vision response — retry")
        finish = getattr(resp.choices[0], "finish_reason", None)
        if finish == "length":
            raise RuntimeError("503 truncated Gemini vision JSON — retry with fewer tokens in prompt")
        try:
            return _parse_vision_json(raw)
        except Exception as exc:
            raise RuntimeError(f"503 invalid Gemini vision JSON: {exc}") from exc

    return call_with_retry(_call, label=f"gemini-vision:{use_model}")


def openai_chat_text(
    *,
    prompt: str,
    model: str | None = None,
    max_tokens: int = 1200,
    temperature: float = 0.3,
) -> str:
    """Text-only chat via OpenAI-compatible Gemini endpoint."""
    from shorts_bot.llm.provider import get_llm_backend

    backend = get_llm_backend()
    if backend is None or backend.provider != "gemini":
        raise RuntimeError("GEMINI_API_KEY required — add in Cursor Secrets")

    use_model = (model or revision_model()).strip()

    def _call():
        resp = backend.client.chat.completions.create(
            model=use_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return (resp.choices[0].message.content or "").strip()

    return call_with_retry(_call, label=f"gemini-text:{use_model}")
