"""Kling 3.0 Short renderer — 2×15s clips, native dialogue audio, one stitch."""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.production.ai_video_guard import require_ai_video_generation

_KLING_NEGATIVE = (
    "on-screen text, subtitles, captions, watermark, logo, cartoon, anime, "
    "CCTV overlay, phone screen UI, cheerful, bright daylight, narrator voiceover"
)

_KLING_VISUAL_PREFIX = (
    "9:16 vertical cinematic horror. Foggy rural American town at night — wet two-lane road, "
    "streetlight pools, abandoned gas station, pine fog, crooked church steeple distant. "
    "Eye worship cult undertones, uncanny villagers, dream invasion. "
    "Real human protagonist (Elliot) in reflections/peripheral when shown. "
    "First-person POV. Photoreal, SCP flash-photo documentary aesthetic, shallow depth of field. "
    "No on-screen text or readable signs."
)


def split_script_parts(hook: str, script: str, *, parts: int = 2) -> list[str]:
    """Split screenplay into N parts for Kling generations (~15s each)."""
    text = f"{hook.strip()} {script.strip()}".strip()
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    if not sentences:
        return [text] * parts if text else [""] * parts
    if len(sentences) <= parts:
        out = sentences + [sentences[-1]] * (parts - len(sentences))
        return out[:parts]
    chunk = max(1, len(sentences) // parts)
    result: list[str] = []
    for i in range(parts):
        start = i * chunk
        end = len(sentences) if i == parts - 1 else min(len(sentences), (i + 1) * chunk)
        result.append(" ".join(sentences[start:end]))
    return result


def build_kling_prompt(
    topic: str,
    script_part: str,
    *,
    part_index: int,
    total_parts: int,
    draft_id: int | None = None,
) -> str:
    from shorts_bot.production.launch_phase import (
        is_silent_launch_draft,
        silent_launch_kling_rules,
    )

    silent = is_silent_launch_draft(draft_id)
    role = (
        "opening hook — impossible visual in the fog"
        if part_index == 0
        else "escalation, rural anomaly, perception break, final sting"
    )
    if silent:
        return (
            f"{_KLING_VISUAL_PREFIX}\n"
            f"Topic: {topic}. Part {part_index + 1}/{total_parts} — {role}.\n"
            f"{silent_launch_kling_rules()}\n"
            f"First-person POV horror — visual actions only (no quoted speech).\n"
            f"Scene actions: {script_part}\n"
            f"Sound: wind, wet gravel, breathing, distant ritual murmur, low horror drone only."
        )
    return (
        f"{_KLING_VISUAL_PREFIX}\n"
        f"Topic: {topic}. Part {part_index + 1}/{total_parts} — {role}.\n"
        f"First-person horror. Character voices only — put spoken lines in quotes. "
        f"No faceless narrator.\n"
        f"Scene: {script_part}\n"
        f"Sound: wind, wood creak, distant ritual murmur, low horror drone."
    )


def build_kling_multi_prompt(script_part: str, *, total_seconds: int) -> list[dict]:
    """Up to 3 internal shots within one 15s Kling generation."""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", script_part) if s.strip()]
    if len(sentences) < 3:
        return [{"prompt": script_part, "duration": total_seconds}]
    third = max(1, len(sentences) // 3)
    groups = [
        " ".join(sentences[:third]),
        " ".join(sentences[third : 2 * third]),
        " ".join(sentences[2 * third :]),
    ]
    per = max(1, total_seconds // 3)
    remainder = total_seconds - per * 2
    return [
        {"prompt": groups[0], "duration": per},
        {"prompt": groups[1], "duration": per},
        {"prompt": groups[2], "duration": remainder},
    ]


def kling_clip_paths(clips_dir: Path, count: int | None = None) -> list[Path]:
    n = count if count is not None else settings.kling_clips_per_short
    return [clips_dir / f"kling_part_{i + 1:02d}.mp4" for i in range(n)]


def _reference_still_from_clip(video_path: Path, clips_dir: Path) -> Path | None:
    """Last frame of prior Kling clip — official API needs an image, not MP4."""
    import subprocess

    if not video_path.exists() or video_path.stat().st_size < 5000:
        return None
    still = clips_dir / f"{video_path.stem}_last.png"
    if still.exists() and still.stat().st_size > 1000:
        return still
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-sseof",
            "-0.05",
            "-i",
            str(video_path),
            "-vframes",
            "1",
            str(still),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return still if still.exists() else None


def render_kling_clips(
    *,
    topic: str,
    hook: str,
    script: str,
    clips_dir: Path,
    reference_image: Path | None = None,
    draft_id: int | None = None,
) -> int:
    """Generate Kling clips (default 2×15s). Returns count written."""
    require_ai_video_generation(action="render_kling_clips")
    from shorts_bot.production.launch_phase import (
        kling_extra_negative_for_draft,
        kling_sound_enabled_for_draft,
    )

    provider = (settings.kling_provider or "official").strip().lower()
    generate_audio = kling_sound_enabled_for_draft(draft_id)
    negative = _KLING_NEGATIVE + kling_extra_negative_for_draft(draft_id)

    clips_dir.mkdir(parents=True, exist_ok=True)
    parts = split_script_parts(hook, script, parts=settings.kling_clips_per_short)
    pace = max(0.0, float(settings.ai_video_pace_sec))
    rendered = 0
    ref_image = reference_image

    for i, part in enumerate(parts):
        dest = clips_dir / f"kling_part_{i + 1:02d}.mp4"
        if dest.exists() and dest.stat().st_size > 10_000:
            rendered += 1
            ref_image = dest
            continue
        if pace and i > 0:
            time.sleep(pace)

        prompt = build_kling_prompt(
            topic, part, part_index=i, total_parts=len(parts), draft_id=draft_id
        )
        multi = (
            build_kling_multi_prompt(part, total_seconds=settings.kling_clip_seconds)
            if settings.kling_multi_shot
            else None
        )
        try:
            start_still = None
            if i > 0 and ref_image:
                start_still = _reference_still_from_clip(ref_image, clips_dir)
            if provider == "official" or settings.has_kling_official:
                from shorts_bot.production.images.kling_official import generate_kling_official_video

                if not settings.has_kling_official:
                    raise RuntimeError(
                        "Kling official selected but KLING_ACCESS_KEY / KLING_SECRET_KEY missing."
                    )
                mode = "pro" if settings.kling_mode.strip().lower() == "pro" else "std"
                generate_kling_official_video(
                    prompt,
                    dest,
                    access_key=settings.kling_access_key or "",
                    secret_key=settings.kling_secret_key or "",
                    model_name=settings.kling_model,
                    duration=settings.kling_clip_seconds,
                    aspect_ratio=settings.kling_aspect_ratio,
                    mode=mode,
                    sound=generate_audio,
                    negative_prompt=negative,
                    multi_prompt=multi,
                    start_image_path=start_still,
                    timeout_sec=settings.ai_video_timeout_sec,
                )
            else:
                token = (settings.replicate_api_token or "").strip()
                if not token:
                    raise RuntimeError(
                        "Kling via Replicate requires REPLICATE_API_TOKEN, or set "
                        "KLING_PROVIDER=official with Kling dev keys."
                    )
                from shorts_bot.production.images.replicate import generate_replicate_kling_video

                generate_replicate_kling_video(
                    prompt,
                    dest,
                    token=token,
                    model=settings.kling_model,
                    duration=settings.kling_clip_seconds,
                    aspect_ratio=settings.kling_aspect_ratio,
                    mode=settings.kling_mode,
                    generate_audio=generate_audio,
                    multi_prompt=multi,
                    start_image_path=start_still,
                    negative_prompt=negative,
                    timeout_sec=settings.ai_video_timeout_sec,
                )
            rendered += 1
            ref_image = dest
        except Exception as exc:
            err = dest.with_suffix(".error.txt")
            err.write_text(str(exc), encoding="utf-8")
            raise

    spec = {
        "backend": "kling",
        "provider": provider if settings.has_kling_official else "replicate",
        "model": settings.kling_model,
        "clips": [
            {
                "file": p.name,
                "prompt": build_kling_prompt(
                    topic, parts[i], part_index=i, total_parts=len(parts), draft_id=draft_id
                ),
                "script_part": parts[i],
            }
            for i, p in enumerate(kling_clip_paths(clips_dir, len(parts)))
        ],
    }
    (clips_dir / "kling_spec.json").write_text(json.dumps(spec, indent=2), encoding="utf-8")
    return rendered
