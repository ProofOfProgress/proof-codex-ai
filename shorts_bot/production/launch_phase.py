"""Launch phase rules — first N Shorts before dialogue and burned-in subtitles unlock."""

from __future__ import annotations

from shorts_bot.config import settings


def launch_silent_video_count() -> int:
    return max(0, int(settings.launch_silent_video_count))


def is_silent_launch_draft(draft_id: int | None) -> bool:
    """Drafts 1..N — no spoken dialogue, no burned captions; ambient + SFX OK."""
    if draft_id is None or draft_id < 1:
        return False
    return draft_id <= launch_silent_video_count()


def should_burn_subtitles(draft_id: int | None) -> bool:
    if is_silent_launch_draft(draft_id):
        return False
    from shorts_bot.production.captions import burn_captions_via_ffmpeg

    return burn_captions_via_ffmpeg() or settings.burn_in_subtitles


def kling_sound_enabled_for_draft(draft_id: int | None) -> bool:
    """Kling native sound track — ambient/diegetic. Speech blocked via prompt on silent launch."""
    return bool(settings.kling_generate_audio)


def skip_narrator_tts(draft_id: int | None) -> bool:
    """Skip Resemble / edge TTS — Kling carries voices, or silent launch has none."""
    if is_silent_launch_draft(draft_id):
        return True
    return settings.uses_kling_native_audio


def skip_transcript_sync(draft_id: int | None) -> bool:
    """Skip Gemini transcript when Kling native audio or silent launch (no captions)."""
    if is_silent_launch_draft(draft_id):
        return True
    return settings.uses_kling_native_audio


def silent_launch_script_rules() -> str:
    return """
LAUNCH PHASE (videos 1–3 — no talking, no subtitles):
- **No spoken dialogue.** No character lines in quotes. No lip-sync speech.
- **Sound is ON** — wind, footsteps, breathing, creaks, ritual murmur, horror sting at end (SFX in post).
- Write **visual action beats** — what the camera (first-person I) sees and does.
- Hook = one impossible **visual** detail (movement in fog, wrong reflection, ritual seen).
- ~70–110 words of scene direction — not conversation.
- Talking + burned-in subtitles unlock on video 4+.
"""


def silent_launch_kling_rules() -> str:
    return (
        "NO SPOKEN DIALOGUE — no lip sync, no mouth talking, no whispered words. "
        "Visual storytelling only. "
        "Audio: ambient wind, wet gravel, breathing, wood creak, distant murmur, horror drone — no human speech."
    )


def kling_extra_negative_for_draft(draft_id: int | None) -> str:
    if not is_silent_launch_draft(draft_id):
        return ""
    return (
        ", spoken dialogue, talking, speech, lip sync, mouth talking, human voice speaking, "
        "whispering words, narrator voiceover"
    )


def next_draft_id_estimate(store) -> int:
    """Highest draft id + 1 (for pre-save script generation)."""
    drafts = store.list_drafts(limit=1)
    return (drafts[0].id + 1) if drafts else 1


def would_be_silent_launch(store=None, *, draft_id: int | None = None) -> bool:
    if draft_id is not None:
        return is_silent_launch_draft(draft_id)
    if store is None:
        return False
    return is_silent_launch_draft(next_draft_id_estimate(store))
