"""Bridge YouTube analytics rewards → Blender param updates (dual learning loop)."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from shorts_bot.config import settings
from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.production.blender.params import BlenderParams, load_params, patch_from_issues, save_params
from shorts_bot.production.blender.trials import BlenderTrialStore
from shorts_bot.rewards.engine import RewardResult


def blender_snapshot_for_pack(pack_dir: Path) -> dict[str, Any]:
    """Params in force at upload — causal link for analytics → Blender grind."""
    store = BlenderTrialStore(pack_dir)
    params = load_params(store.best_path) or BlenderParams.defaults()
    return {
        "blender_rl": {
            "params": params.to_env(),
            "best_path": str(store.best_path),
        }
    }


def youtube_reward_to_visual_issues(reward: RewardResult) -> list[str]:
    """Map retention/swipe-away diagnosis → vision-style issue strings for param patches."""
    issues: list[str] = []
    blob = f"{reward.reason} {reward.diagnosis}".lower()
    if reward.verdict == "punish":
        if "swipe" in blob or "hook" in blob or "viewed" in blob:
            issues.extend(["face not close enough", "weak hooks framing"])
        if "retention" in blob or "pacing" in blob or "payoff" in blob:
            issues.extend(["mouth not visible", "jumpscare payoff weak"])
        if "like" in blob or "engagement" in blob:
            issues.append("composition not compelling")
    elif reward.verdict == "reward":
        if "retention" in blob or "swipe" in blob:
            issues.append("keep mouth red framing strong")
    return issues


def _match_upload_draft(memory: MemoryExtensions, reward: RewardResult) -> int | None:
    from shorts_bot.learning.reflect import _match_upload

    upload = _match_upload(memory, reward.video_label, metrics=reward.metrics)
    if not upload:
        return None
    draft_id = upload.get("draft_id")
    return int(draft_id) if draft_id is not None else None


def _grind_due(memory: MemoryExtensions) -> bool:
    raw = memory.get_training_config("last_blender_grind") or ""
    if not raw.strip():
        return True
    try:
        last = float(raw)
    except ValueError:
        return True
    interval_h = max(1, settings.blender_self_train_interval_hours)
    return (time.time() - last) >= interval_h * 3600


def _seed_params_from_upload(
    memory: MemoryExtensions,
    draft_id: int,
    scored: list[RewardResult],
) -> BlenderParams:
    pack = settings.data_dir / "production" / f"draft_{draft_id}"
    store = BlenderTrialStore(pack)
    base = load_params(store.best_path) or BlenderParams.defaults()

    for reward in scored:
        if _match_upload_draft(memory, reward) != draft_id:
            continue
        issues = youtube_reward_to_visual_issues(reward)
        if issues:
            base = patch_from_issues(base, issues)
        if reward.verdict == "reward":
            memory.set_training_config(
                f"repeat:blender-draft-{draft_id}",
                f"YouTube reward — keep params cam_z={base.camera_z:.2f} face={base.face_scale:.2f}",
            )
    return base.clamp()


def pick_grind_draft(memory: MemoryExtensions, scored: list[RewardResult]) -> tuple[int, str]:
    """Prefer punished upload draft; else default lab draft."""
    for reward in sorted(scored, key=lambda r: r.score):
        if reward.verdict != "punish":
            continue
        draft_id = _match_upload_draft(memory, reward)
        if draft_id is not None:
            return draft_id, f"YouTube punish on «{reward.video_label[:40]}»"
    return settings.blender_self_train_default_draft_id, "scheduled grind"


def maybe_grind_after_analytics(
    memory: MemoryExtensions,
    scored: list[RewardResult] | None,
) -> str:
    """
    After 12h analytics sync: optionally run Blender self-train trials.
    Keeps YouTube retention/swipe learning + Blender vision loop linked.
    """
    if not settings.blender_self_train_enabled or not settings.blender_self_train_auto_grind:
        return ""
    if not settings.blender_self_train_on_sync:
        return ""

    scored = scored or []
    has_punish = any(r.verdict == "punish" for r in scored)
    if not has_punish and not _grind_due(memory):
        return ""

    draft_id, reason = pick_grind_draft(memory, scored)
    pack = settings.data_dir / "production" / f"draft_{draft_id}"
    seed = _seed_params_from_upload(memory, draft_id, scored)
    seed_path = pack / "blender_rl" / "seed_from_youtube.json"
    save_params(seed_path, seed, meta={"reason": reason, "source": "youtube_analytics"})

    trials = max(1, settings.blender_self_train_trials_on_sync)
    from shorts_bot.production.blender.self_train import run_blender_self_train

    result = run_blender_self_train(
        draft_id,
        pack_dir=pack,
        trials=trials,
        topic=f"draft {draft_id} analytics grind",
    )
    memory.set_training_config("last_blender_grind", str(time.time()))
    memory.set_training_config(
        f"applied:blender-youtube-{draft_id}",
        f"{reason} → best {result.best_score:.2f}/10",
    )
    return result.message


def run_scheduled_grind(memory: MemoryExtensions | None = None) -> str:
    """Standalone grind (same interval gate) — for background loop."""
    if memory is None:
        from shorts_bot.memory.store import MemoryStore

        memory = MemoryExtensions(MemoryStore(settings.database_path))
    return maybe_grind_after_analytics(memory, scored=[])
