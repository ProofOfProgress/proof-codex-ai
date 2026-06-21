"""Public workflow evolution — TextGrad (EvoAgentX stack) + safe fallbacks."""

from __future__ import annotations

import logging
import re

from shorts_bot.config import settings
from shorts_bot.learning.workflow import HOOK_TEMPLATES

logger = logging.getLogger(__name__)

_CREDIT_FAIL = re.compile(r"\b(credit|upgrade|paywall|subscription|payment)\b", re.I)
_RENDER_TIMEOUT = re.compile(r"\b(timeout|timed out|expect_download)\b", re.I)


def next_hook_template(current: str) -> str:
    pool = list(HOOK_TEMPLATES)
    if current in pool:
        return pool[(pool.index(current) + 1) % len(pool)]
    return pool[0]


def optimize_hook_template(current: str, feedback: str) -> str | None:
    """
    TextGrad prompt evolution (used by EvoAgentX internally).
    Returns improved hook template or None if optimization unavailable.
    """
    if not settings.textgrad_evolution_enabled:
        return None
    if not (settings.has_gemini or settings.has_openai):
        return None
    if "{product}" not in current:
        current = current + " {product}"

    try:
        import textgrad as tg
        from textgrad.engine_experimental.litellm import LiteLLMEngine
    except ImportError:
        logger.warning("textgrad not installed")
        return None

    model = f"gemini/{settings.gemini_model}" if settings.has_gemini else "gpt-4.1-nano-2025-04-14"
    try:
        engine = LiteLLMEngine(model_string=model)
        tg.set_backward_engine(engine)
        hook = tg.Variable(
            current,
            requires_grad=True,
            role_description=(
                "YouTube Short hook template for 30s AI product review. "
                "Must contain {product} placeholder exactly once. Under 15 words."
            ),
        )
        optimizer = tg.TGD(parameters=[hook])
        loss_fn = tg.TextLoss(
            f"YouTube analytics: {feedback[:400]}. Improve hook to stop scroll.",
            engine=engine,
        )
        loss = loss_fn(hook)
        loss.backward()
        optimizer.step()
        candidate = (hook.value or "").strip()
        if candidate and "{product}" in candidate and len(candidate) < 120:
            return candidate
    except Exception as exc:
        logger.warning("TextGrad hook evolution failed: %s", exc)
    return None


def evolve_hook_after_punish(current: str, feedback: str) -> tuple[str, str]:
    """Returns (new_template, method) where method is textgrad|rotate."""
    improved = optimize_hook_template(current, feedback)
    if improved and improved != current:
        return improved, "textgrad"
    rotated = next_hook_template(current)
    return rotated, "rotate"


def match_credit_fail(detail: str) -> bool:
    return bool(_CREDIT_FAIL.search(detail))


def match_render_timeout(detail: str) -> bool:
    return bool(_RENDER_TIMEOUT.search(detail))
