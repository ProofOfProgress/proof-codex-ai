"""Horror voice drift detection and auto-repair before expensive pipeline steps."""

from __future__ import annotations

from dataclasses import dataclass

from shorts_bot.config import settings
from shorts_bot.drafts.generator import DraftGenerator
from shorts_bot.memory.store import MemoryStore
from shorts_bot.production.horror_repair import script_needs_horror_repair
from shorts_bot.production.jenny_checks import check_jenny_voice


@dataclass
class HorrorGuardResult:
    hook: str
    script: str
    help_angle: str
    repaired: bool
    message: str


def _offline_fix(store: MemoryStore, draft_id: int, topic: str, help_angle: str) -> HorrorGuardResult:
    from shorts_bot.config import settings
    from shorts_bot.production.pipeline_integrity import (
        clear_render_artifacts,
        invalidate_downstream_steps,
        write_content_stamp,
    )

    gen = DraftGenerator(store)
    fixed = gen._generate_offline(topic, help_angle)  # noqa: SLF001
    lower_topic = (topic or "").lower()
    if any(k in lower_topic for k in ("security", "camera", "motion")):
        if "your" not in fixed.hook.lower() or fixed.script.lstrip().startswith("["):
            fixed.hook = "Your security camera flagged motion at 3:12 AM. You live alone."
            fixed.script = (
                f"{fixed.hook} "
                "The hallway was empty. You told yourself it was a glitch. "
                "Then the motion box locked onto the closet door. "
                "The room stayed still for one whole second. "
                "On the recording, something crawled out before the door opened in real life. "
                "It looked straight into the camera. Then it lunged."
            )
    store.update_draft_content(
        draft_id,
        script=fixed.script,
        hook=fixed.hook,
        help_angle=fixed.help_angle,
    )
    if fixed.visual_beats:
        from shorts_bot.drafts.meta import save_draft_meta

        save_draft_meta(draft_id, visual_beats=fixed.visual_beats)
    pack = settings.data_dir / "production" / f"draft_{draft_id}"
    cleared = clear_render_artifacts(pack)
    invalidate_downstream_steps(pack, draft_id)
    write_content_stamp(pack, hook=fixed.hook, script=fixed.script)
    cleared_note = f" Cleared {len(cleared)} stale artifact(s)." if cleared else ""
    return HorrorGuardResult(
        hook=fixed.hook,
        script=fixed.script,
        help_angle=fixed.help_angle,
        repaired=True,
        message=f"Auto-repaired horror voice drift (offline second-person template).{cleared_note}",
    )


def ensure_horror_voice_before_pipeline(
    store: MemoryStore,
    draft_id: int,
    *,
    hook: str,
    script: str,
    help_angle: str,
    topic: str,
) -> HorrorGuardResult:
    """Fix first-person drift before TTS/I2V spend."""
    if not settings.pipeline_auto_horror_repair:
        return HorrorGuardResult(hook, script, help_angle, False, "Horror auto-repair disabled.")
    if script_needs_horror_repair(script, hook) or check_jenny_voice(script, hook):
        return _offline_fix(store, draft_id, topic, help_angle)
    return HorrorGuardResult(hook, script, help_angle, False, "Horror voice OK.")


def guard_after_humanize(
    store: MemoryStore,
    draft_id: int,
    *,
    hook: str,
    script: str,
    help_angle: str,
    topic: str,
) -> HorrorGuardResult:
    """Re-check after LLM humanize; repair if drift reintroduced."""
    if not settings.pipeline_block_voice_drift:
        return HorrorGuardResult(hook, script, help_angle, False, "Post-humanize drift check disabled.")
    issues = check_jenny_voice(script, hook)
    drift = script_needs_horror_repair(script, hook)
    if not issues and not drift:
        return HorrorGuardResult(hook, script, help_angle, False, "Humanize passed horror voice check.")
    if settings.pipeline_auto_horror_repair:
        return _offline_fix(store, draft_id, topic, help_angle)
    detail = "; ".join(issues) if issues else "first-person drift detected"
    raise RuntimeError(f"Horror voice guard failed after humanize: {detail}")
