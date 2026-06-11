"""Block paid Replicate I2V / FLUX generation unless explicitly enabled."""

from __future__ import annotations

from shorts_bot.config import settings


def ai_video_generation_enabled() -> bool:
    return bool(settings.ai_video_generation_enabled)


def require_ai_video_generation(*, action: str) -> None:
    """Raise when owner has paused video generation (assemble-from-cache OK)."""
    if ai_video_generation_enabled():
        return
    raise RuntimeError(
        f"AI video generation is disabled ({action}). "
        "Use render-only on existing clips: "
        "python3 -m shorts_bot.production.render_pack_cli --draft-id N. "
        "To allow new I2V/FLUX, set AI_VIDEO_GENERATION_ENABLED=true in .env."
    )
