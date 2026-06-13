"""Kling Short renderer — multi-clip stitch, launch-silent or dialogue modes."""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.production.ai_video_guard import require_ai_video_generation

_KLING_NEGATIVE = (
    "on-screen text, subtitles, captions, watermark, logo, cartoon, anime, "
    "CCTV overlay, phone screen UI, cheerful, bright daylight, narrator voiceover, "
    "static photo, slideshow, frozen frame, talking, speech"
)

_KLING_RURAL_PREFIX = (
    "9:16 vertical cinematic horror MOVIE — constant motion, handheld POV, never static. "
    "Foggy rural American town at night — wet two-lane road, abandoned gas station, pine fog. "
    "Photoreal, shallow depth of field, SCP documentary dread, theatrical horror film energy."
)

_FORM2_ENTITY = (
    "Form 2 rural anomaly — too tall, wrong joints, elongated limbs, SCP flash-photo wrongness, "
    "uncanny humanoid, not a normal villager"
)


def split_script_parts(hook: str, script: str, *, parts: int = 2) -> list[str]:
    """Split screenplay into N parts for Kling generations."""
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
    if silent:
        roles = [
            (
                "OPEN — handheld POV pushes down foggy rural road. Sodium streetlight FLICKERS "
                f"strobing orange. Between flickers: {_FORM2_ENTITY} glimpsed at road edge. "
                "Camera never stops moving — drift, breathe, step forward."
            ),
            (
                "ESCALATION — streetlight flicker faster. Entity TELEPORTS closer each time light dies — "
                "only moves in darkness. Stands at gas pumps, dead center, waves slowly with broken creepy "
                "wrist. Light OFF: entity jumps forward. Light ON: closer. Handheld orbit."
            ),
            (
                "FINALE — entity fills frame center, waves creepily directly at camera. Flicker sync: "
                "frozen in light, moves in black. Final flicker blackout then LUNGE at lens. "
                "Movie sting energy."
            ),
        ]
        role = roles[min(part_index, len(roles) - 1)]
        return (
            f"{_KLING_RURAL_PREFIX}\n"
            f"{silent_launch_kling_rules()}\n"
            f"Part {part_index + 1}/{total_parts} — {role}\n"
            f"Visual beats: {script_part}\n"
            f"NO AUDIO FROM CHARACTERS — video silent; wind/SFX added in post."
        )
    return (
        f"{_KLING_RURAL_PREFIX}\n"
        f"Topic: {topic}. Part {part_index + 1}/{total_parts}.\n"
        f"First-person horror. Character voices only — spoken lines in quotes. No narrator.\n"
        f"Scene: {script_part}\n"
        f"Sound: wind, wood creak, distant murmur, low horror drone."
    )


def build_kling_multi_prompt(
    script_part: str,
    *,
    total_seconds: int,
    part_index: int = 0,
    draft_id: int | None = None,
) -> list[dict]:
    """Motion-heavy internal cuts — 3 shots per clip for silent launch."""
    from shorts_bot.production.launch_phase import is_silent_launch_draft

    per = max(3, total_seconds // 3)
    remainder = max(1, total_seconds - per * 2)

    if is_silent_launch_draft(draft_id):
        silent_shots = [
            [
                (
                    f"Handheld POV walking forward on wet rural road, camera sway, "
                    f"flickering streetlight strobes — {_FORM2_ENTITY} flash-visible in fog"
                ),
                (
                    "Camera pushes faster, light flickers OFF then ON — entity closer each pulse, "
                    "jerky unnatural movement between frames"
                ),
                (
                    f"Close approach to gas station, entity silhouette waves one wrong arm, "
                    "continuous handheld motion"
                ),
            ],
            [
                (
                    f"Entity stands center frame at pumps, slow creepy wave, broken joints, "
                    "streetlight flicker strobing — entity frozen in light"
                ),
                (
                    "Light dies — entity teleports three meters closer in darkness — light returns, "
                    "handheld camera pulls back then pushes in"
                ),
                (
                    f"Orbiting handheld around {_FORM2_ENTITY}, wave continues, fog swirls, "
                    "never static"
                ),
            ],
            [
                (
                    f"{_FORM2_ENTITY} fills frame, waves directly at camera, flicker sync — "
                    "only moves when light off"
                ),
                (
                    "Streetlight dies long beat — entity lunges forward in black — light snaps ON "
                    "inches from lens"
                ),
                (
                    "Final lunge at camera, motion blur, horror movie jump scare, handheld shake"
                ),
            ],
        ]
        shots = silent_shots[min(part_index, 2)]
        return [
            {"prompt": shots[0], "duration": per},
            {"prompt": shots[1], "duration": per},
            {"prompt": shots[2], "duration": remainder},
        ]

    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", script_part) if s.strip()]
    if len(sentences) < 3:
        return [{"prompt": script_part, "duration": total_seconds}]
    third = max(1, len(sentences) // 3)
    groups = [
        " ".join(sentences[:third]),
        " ".join(sentences[third : 2 * third]),
        " ".join(sentences[2 * third :]),
    ]
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
    force_regen: bool = False,
) -> int:
    """Generate Kling clips. Returns count written."""
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
        if (
            not force_regen
            and dest.exists()
            and dest.stat().st_size > 10_000
            and not dest.with_suffix(".error.txt").exists()
        ):
            rendered += 1
            ref_image = dest
            continue
        if pace and i > 0:
            time.sleep(pace)

        prompt = build_kling_prompt(
            topic, part, part_index=i, total_parts=len(parts), draft_id=draft_id
        )
        multi = (
            build_kling_multi_prompt(
                part,
                total_seconds=settings.kling_clip_seconds,
                part_index=i,
                draft_id=draft_id,
            )
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
                mode_raw = (settings.kling_mode or "std").strip().lower()
                mode = "pro" if mode_raw in {"pro", "1080p"} else "std"
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
            dest.with_suffix(".error.txt").unlink(missing_ok=True)
        except Exception as exc:
            err = dest.with_suffix(".error.txt")
            err.write_text(str(exc), encoding="utf-8")
            raise

    spec = {
        "backend": "kling",
        "provider": provider if settings.has_kling_official else "replicate",
        "model": settings.kling_model,
        "mode": settings.kling_mode,
        "sound": generate_audio,
        "draft_id": draft_id,
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
