"""Assemble final 9:16 Short MP4 from production pack (ffmpeg)."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RenderedVideo:
    draft_id: int
    output_path: Path
    duration_seconds: float
    message: str


def _mix_jumpscare_sting(
    audio_path: Path,
    *,
    duration: float,
    sting_start: float | None = None,
) -> Path:
    """Layer a synthetic noise sting a couple seconds before the end (finale drafts only)."""
    from shorts_bot.config import settings

    if not settings.jumpscare_sting_enabled or duration <= 1.0:
        return audio_path

    sting_dur = min(settings.jumpscare_sting_seconds, duration * 0.45)
    if sting_start is None:
        sting_start = max(0.0, duration - sting_dur)
    else:
        sting_start = max(0.0, min(sting_start, duration - 0.25))
        sting_dur = min(sting_dur, duration - sting_start)
    delay_ms = int(sting_start * 1000)
    fade_out_start = max(0.08, sting_dur - 0.18)
    sting_src = (
        f"anoisesrc=color=white:duration={sting_dur:.3f}:sample_rate=48000,"
        f"highpass=f=900,lowpass=f=9000,volume={settings.jumpscare_sting_gain},"
        f"afade=t=in:st=0:d=0.04,afade=t=out:st={fade_out_start:.3f}:d=0.16"
    )
    filter_complex = (
        f"[1:a]adelay={delay_ms}|{delay_ms}[sting];"
        f"[0:a][sting]amix=inputs=2:duration=first:dropout_transition=0:"
        f"weights=1 {settings.jumpscare_sting_mix}[out]"
    )
    out_path = audio_path.parent / "_voiceover_stung.mp3"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(audio_path),
            "-f",
            "lavfi",
            "-i",
            sting_src,
            "-filter_complex",
            filter_complex,
            "-map",
            "[out]",
            "-c:a",
            "libmp3lame",
            "-b:a",
            f"{settings.video_audio_bitrate_k}k",
            str(out_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return out_path


def _probe_duration(audio_path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(audio_path),
        ],
        text=True,
    )
    return float(out.strip())


def _scaled_durations(segments: list[dict], audio_duration: float) -> list[float]:
    manifest_total = segments[-1]["end_seconds"]
    if manifest_total <= 0:
        raise ValueError("Invalid segment timing in manifest.")
    scale = audio_duration / manifest_total
    durs: list[float] = []
    for seg in segments:
        raw = seg["end_seconds"] - seg["start_seconds"]
        durs.append(max(0.35, raw * scale))
    # Normalize so sum matches audio exactly
    total = sum(durs)
    if total > 0:
        fix = audio_duration / total
        durs = [d * fix for d in durs]
    return durs


def _write_concat(images_dir: Path, segments: list[dict], durations: list[float], concat_path: Path) -> None:
    lines = ["ffconcat version 1.0"]
    for seg, dur in zip(segments, durations):
        img = images_dir / seg["filename"]
        if not img.exists():
            raise FileNotFoundError(f"Missing image: {img}")
        lines.append(f"file '{img.resolve()}'")
        lines.append(f"duration {dur:.4f}")
    last = (images_dir / segments[-1]["filename"]).resolve()
    lines.append(f"file '{last}'")
    concat_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _ken_burns_zoompan(duration: float, *, zoom_motion: str, width: int, height: int) -> str:
    """Subtle zoom per still — retention lift without CapCut."""
    frames = max(1, int(duration * 30))
    if zoom_motion == "out":
        z = "if(lte(zoom,1.0),1.06,max(1.001,zoom-0.0004))"
    elif zoom_motion == "in":
        z = "min(zoom+0.0004,1.06)"
    else:
        return f"scale={width}:{height}:flags=lanczos,format=yuv420p"
    return (
        f"scale={width}:{height}:flags=lanczos,"
        f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d={frames}:s={width}x{height}:fps=30,format=yuv420p"
    )


def _render_motion_clips(
    images_dir: Path,
    segments: list[dict],
    durations: list[float],
    *,
    zoom_motion: str,
    tmp_dir: Path,
    width: int,
    height: int,
) -> Path:
    """Pre-render each still to a short MP4 with optional Ken Burns."""
    tmp_dir.mkdir(parents=True, exist_ok=True)
    clip_paths: list[Path] = []
    for i, (seg, dur) in enumerate(zip(segments, durations)):
        img = images_dir / seg["filename"]
        clip = tmp_dir / f"clip_{i:03d}.mp4"
        vf = _ken_burns_zoompan(dur, zoom_motion=zoom_motion, width=width, height=height)
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-loop",
                "1",
                "-t",
                f"{dur:.4f}",
                "-i",
                str(img.resolve()),
                "-vf",
                vf,
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-pix_fmt",
                "yuv420p",
                "-an",
                str(clip),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        clip_paths.append(clip)

    concat_path = tmp_dir / "_clips_concat.txt"
    lines = ["ffconcat version 1.0"]
    for clip in clip_paths:
        lines.append(f"file '{clip.resolve()}'")
    concat_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    silent_video = tmp_dir / "_video_silent.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_path),
            "-c",
            "copy",
            str(silent_video),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return silent_video



def _suspense_replay_filter(duration: float, *, width: int, height: int) -> str:
    """Slow zoom-out hold on finale — no scare, bait Shorts replay."""
    frames = max(1, int(duration * 30))
    return (
        f"scale={width}:{height}:flags=lanczos,"
        f"zoompan=z='if(lte(zoom,1.0),1.05,max(1.001,zoom-0.00035))':"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d={frames}:s={width}x{height}:fps=30,"
        f"eq=brightness=-0.06:contrast=1.12:saturation=0.92,"
        f"format=yuv420p"
    )


def _jumpscare_video_filter(duration: float, *, width: int, height: int) -> str:
    """Rapid zoom + brightness pulse so the scare has a visible pop, not audio-only static."""
    frames = max(1, int(duration * 30))
    flash_start = max(0.0, duration - 0.28)
    return (
        f"scale={width}:{height}:flags=lanczos,"
        f"zoompan=z='min(zoom+0.028,2.9)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d={frames}:s={width}x{height}:fps=30,"
        f"eq=brightness='if(between(t,{flash_start:.3f},{duration:.3f}),"
        f"1.1*sin(50*PI*t)+1.1,0)':contrast=1.35:saturation=1.15,"
        f"format=yuv420p"
    )


def _trim_scale_clip(
    src: Path,
    dest: Path,
    *,
    duration: float,
    width: int,
    height: int,
    jumpscare: bool = False,
    suspense_replay: bool = False,
) -> None:
    if jumpscare:
        vf = _jumpscare_video_filter(duration, width=width, height=height)
    elif suspense_replay:
        vf = _suspense_replay_filter(duration, width=width, height=height)
    else:
        vf = f"scale={width}:{height}:flags=lanczos,format=yuv420p"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(src.resolve()),
            "-t",
            f"{duration:.4f}",
            "-vf",
            vf,
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-pix_fmt",
            "yuv420p",
            str(dest),
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def _nearest_still_image(images_dir: Path, stem: str) -> Path | None:
    """When transcript resync renames the final segment stem, use closest timestamp still."""
    try:
        target = float(stem)
    except ValueError:
        return None
    candidates: list[tuple[float, Path]] = []
    for path in images_dir.glob("*.png"):
        try:
            candidates.append((float(path.stem), path))
        except ValueError:
            continue
    if not candidates:
        return None
    candidates.sort(key=lambda row: abs(row[0] - target))
    return candidates[0][1]


def _still_to_clip(
    src: Path,
    dest: Path,
    *,
    duration: float,
    width: int,
    height: int,
    jumpscare: bool = False,
    suspense_replay: bool = False,
) -> None:
    """Hold a FLUX still for segment duration when I2V clip is capped/missing."""
    if jumpscare:
        vf = _jumpscare_video_filter(duration, width=width, height=height)
    elif suspense_replay:
        vf = _suspense_replay_filter(duration, width=width, height=height)
    else:
        vf = f"scale={width}:{height}:flags=lanczos,format=yuv420p"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-i",
            str(src.resolve()),
            "-t",
            f"{duration:.4f}",
            "-vf",
            vf,
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-pix_fmt",
            "yuv420p",
            str(dest),
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def _render_from_video_clips(
    clips_dir: Path,
    images_dir: Path,
    segments: list[dict],
    durations: list[float],
    *,
    tmp_dir: Path,
    width: int,
    height: int,
    jumpscare_segment_index: int | None = None,
    suspense_replay: bool = False,
    screen_text_specs: list | None = None,
    caption_segments: list[dict] | None = None,
    hook: str = "",
    topic: str = "",
) -> Path:
    from shorts_bot.config import settings
    from shorts_bot.production.screen_text_overlay import maybe_apply_screen_text

    tmp_dir.mkdir(parents=True, exist_ok=True)
    overlay_specs = screen_text_specs or []
    captions = caption_segments or []
    clip_paths: list[Path] = []
    still_fallbacks = 0
    last_i = len(segments) - 1
    for i, (seg, dur) in enumerate(zip(segments, durations)):
        stem = Path(seg["filename"]).stem
        src = clips_dir / f"{stem}.mp4"
        clip = tmp_dir / f"clip_{i:03d}.mp4"
        scare_beat = (
            jumpscare_segment_index is not None
            and i == jumpscare_segment_index
        )
        use_dedicated_scare = (
            scare_beat
            and settings.jumpscare_dedicated_clip
        )
        replay_hold = suspense_replay and i == last_i and not scare_beat
        if use_dedicated_scare:
            from shorts_bot.production.jumpscare_clip import (
                compose_finale_jumpscare_segment,
                jumpscare_clip_path,
            )

            scare_src = jumpscare_clip_path(clips_dir)
            if not scare_src.exists() or scare_src.stat().st_size < 5000:
                raise FileNotFoundError(
                    f"Missing dedicated jumpscare video at {scare_src}. "
                    "Run: python3 -m shorts_bot.production.render_jumpscare_cli --draft-id N --force"
                )
            prev_still = None
            prev_clip = None
            if i > 0:
                prev = segments[i - 1]
                prev_still = images_dir / prev["filename"]
                prev_clip = clips_dir / f"{Path(prev['filename']).stem}.mp4"
            compose_finale_jumpscare_segment(
                jumpscare_src=scare_src,
                dest=clip,
                segment_duration=dur,
                setup_still=prev_still,
                setup_clip=prev_clip if prev_clip and prev_clip.exists() else None,
                width=width,
                height=height,
            )
        elif src.exists():
            zoom_scare = scare_beat and (
                settings.jumpscare_visual_flash or settings.jumpscare_dedicated_clip
            )
            _trim_scale_clip(
                src,
                clip,
                duration=dur,
                width=width,
                height=height,
                jumpscare=zoom_scare,
                suspense_replay=replay_hold,
            )
        else:
            still = images_dir / seg["filename"]
            if not still.exists():
                alt = _nearest_still_image(images_dir, stem)
                if alt is None:
                    raise FileNotFoundError(f"Missing motion clip and still: {src} / {still}")
                still = alt
            _still_to_clip(
                still,
                clip,
                duration=dur,
                width=width,
                height=height,
                jumpscare=scare_beat and settings.jumpscare_visual_flash,
                suspense_replay=replay_hold,
            )
            still_fallbacks += 1
        spec = overlay_specs[i] if i < len(overlay_specs) else None
        if settings.screen_text_overlay_enabled and (spec is not None or captions):
            clip = maybe_apply_screen_text(
                clip,
                spec,
                tmp_dir=tmp_dir,
                segment_index=i,
                segment=seg,
                captions=captions if captions else None,
                hook=hook,
                topic=topic,
            )
        clip_paths.append(clip)
    if still_fallbacks:
        note = tmp_dir / "_hybrid_still_fallbacks.txt"
        note.write_text(f"{still_fallbacks} segment(s) used FLUX stills (I2V cap)\n", encoding="utf-8")
    concat_path = tmp_dir / "_clips_concat.txt"
    lines = ["ffconcat version 1.0"]
    for clip in clip_paths:
        lines.append(f"file '{clip.resolve()}'")
    concat_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    silent_video = tmp_dir / "_video_silent.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_path),
            "-c",
            "copy",
            str(silent_video),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return silent_video


def render_short_video(
    pack_dir: Path,
    *,
    draft_id: int,
    audio_name: str = "voiceover.mp3",
    output_name: str = "final_short.mp4",
    caption_y_offset: int = 0,
    zoom_motion: str = "none",
) -> RenderedVideo:
    """Build H.264 Short from manifest segments + voiceover audio."""
    manifest_path = pack_dir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"No manifest at {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    segments = manifest.get("segments") or []
    if not segments:
        raise ValueError("Manifest has no segments.")

    audio_path = pack_dir / audio_name
    if not audio_path.exists():
        raise FileNotFoundError(f"No audio at {audio_path}")

    images_dir = pack_dir / "images"
    audio_duration = _probe_duration(audio_path)

    from shorts_bot.production.segment_sync import normalize_segment_timeline

    segments = normalize_segment_timeline(segments, audio_duration)

    from shorts_bot.production.jumpscare_timing import (
        JumpscarePlan,
        load_plan_for_draft,
        sting_start_seconds,
    )

    plan_raw = manifest.get("jumpscare_plan")
    plan = (
        JumpscarePlan.from_dict(plan_raw)
        if plan_raw
        else load_plan_for_draft(draft_id, len(segments))
    )
    jumpscare_segment_index = (
        plan.primary_segment_index if plan.has_jumpscare else None
    )
    suspense_replay = plan.profile == "suspense_replay"
    from shorts_bot.config import settings

    if settings.horror_sfx_enabled:
        from shorts_bot.production.horror_sfx_mix import apply_horror_sfx_to_pack_audio

        audio_path = apply_horror_sfx_to_pack_audio(
            pack_dir,
            segments,
            plan,
            audio_path,
            audio_duration=audio_duration,
        )
        if audio_path.name == "_voiceover_sfx.mp3":
            audio_duration = _probe_duration(audio_path)
    else:
        sting_start = sting_start_seconds(
            plan, segments=segments, total_duration=audio_duration
        )
        if sting_start is not None and settings.jumpscare_sting_enabled:
            audio_path = _mix_jumpscare_sting(
                audio_path, duration=audio_duration, sting_start=sting_start
            )
            if audio_path.name == "_voiceover_stung.mp3":
                audio_duration = _probe_duration(audio_path)
    durations = _scaled_durations(segments, audio_duration)

    out_path = pack_dir / output_name

    from shorts_bot.config import settings
    from shorts_bot.production.caption_timing import resolve_caption_segments
    from shorts_bot.production.captions import burn_captions_via_ffmpeg
    from shorts_bot.production.subtitles import ffmpeg_subtitles_filter, write_subtitle_files

    caption_segments = resolve_caption_segments(
        pack_dir=pack_dir,
        script=str(manifest.get("script") or ""),
        audio_duration=audio_duration,
    )
    if not caption_segments:
        caption_segments = [
            {
                "start_seconds": s["start_seconds"],
                "end_seconds": s["end_seconds"],
                "spoken_text": s.get("spoken_text", ""),
            }
            for s in segments
        ]
    (pack_dir / "caption_segments.json").write_text(
        __import__("json").dumps(caption_segments, indent=2),
        encoding="utf-8",
    )
    from shorts_bot.production.variety import variety_for_draft

    variety = variety_for_draft(draft_id)
    effective_caption_y = caption_y_offset + variety.caption_y_offset

    ass_path = write_subtitle_files(
        pack_dir,
        caption_segments,
        audio_duration,
        caption_y_offset=effective_caption_y,
    )

    from shorts_bot.production.framing import FRAME_HEIGHT, FRAME_WIDTH

    render_mode = manifest.get("render_mode") or "slideshow"
    if render_mode == "video_clips":
        clips_dir = pack_dir / "clips"
        if (
            plan.has_jumpscare
            and settings.jumpscare_dedicated_clip
            and settings.jumpscare_auto_generate
        ):
            from shorts_bot.production.jumpscare_clip import ensure_jumpscare_video_clip

            ensure_jumpscare_video_clip(pack_dir)
        from shorts_bot.production.screen_text_spec import (
            overlays_for_segments,
            write_overlay_manifest,
        )

        screen_specs = overlays_for_segments(
            segments,
            visual_beats=manifest.get("visual_beats"),
            hook=str(manifest.get("hook") or ""),
            topic=str(manifest.get("topic") or ""),
        )
        write_overlay_manifest(pack_dir, screen_specs)
        silent = _render_from_video_clips(
            clips_dir,
            images_dir,
            segments,
            durations,
            tmp_dir=pack_dir / "_motion_clips",
            width=FRAME_WIDTH,
            height=FRAME_HEIGHT,
            jumpscare_segment_index=jumpscare_segment_index,
            suspense_replay=suspense_replay,
            screen_text_specs=screen_specs,
            caption_segments=caption_segments,
            hook=str(manifest.get("hook") or ""),
            topic=str(manifest.get("topic") or ""),
        )
        video_input = ["-i", str(silent)]
        vf_parts: list[str] = []
        if burn_captions_via_ffmpeg() or settings.burn_in_subtitles:
            vf_parts.append(ffmpeg_subtitles_filter(ass_path).split(",", 1)[1])
        vf = ",".join(vf_parts) if vf_parts else None
        cmd = ["ffmpeg", "-y", *video_input, "-i", str(audio_path)]
        if vf:
            cmd.extend(["-vf", vf])
        cmd.extend(
            [
                "-c:v",
                "libx264",
                "-preset",
                settings.video_preset,
                "-crf",
                str(settings.video_crf),
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-b:a",
                f"{settings.video_audio_bitrate_k}k",
                "-ar",
                "48000",
                "-movflags",
                "+faststart",
                "-t",
                f"{audio_duration:.3f}",
                str(out_path),
            ]
        )
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return RenderedVideo(
            draft_id=draft_id,
            output_path=out_path,
            duration_seconds=audio_duration,
            message=(
                f"Rendered {out_path.name} ({audio_duration:.1f}s, 1080×1920, AI video clips). "
                f"Captions: ffmpeg ASS burn-in + captions.srt for YouTube."
            ),
        )

    use_motion = settings.video_ken_burns and zoom_motion in ("in", "out")
    if use_motion:
        silent = _render_motion_clips(
            images_dir,
            segments,
            durations,
            zoom_motion=zoom_motion,
            tmp_dir=pack_dir / "_motion_clips",
            width=FRAME_WIDTH,
            height=FRAME_HEIGHT,
        )
        video_input = ["-i", str(silent)]
    else:
        concat_path = pack_dir / "_concat.txt"
        _write_concat(images_dir, segments, durations, concat_path)
        video_input = ["-f", "concat", "-safe", "0", "-i", str(concat_path)]

    vf_parts: list[str] = []
    if not use_motion:
        vf_parts.extend([f"scale={FRAME_WIDTH}:{FRAME_HEIGHT}:flags=lanczos", "format=yuv420p"])
    if burn_captions_via_ffmpeg() or settings.burn_in_subtitles:
        vf_parts.append(ffmpeg_subtitles_filter(ass_path).split(",", 1)[1])
    vf = ",".join(vf_parts) if vf_parts else None

    cmd = ["ffmpeg", "-y", *video_input, "-i", str(audio_path)]
    if vf:
        cmd.extend(["-vf", vf])
    cmd.extend(
        [
            "-c:v",
            "libx264",
            "-preset",
            settings.video_preset,
            "-crf",
            str(settings.video_crf),
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            f"{settings.video_audio_bitrate_k}k",
            "-ar",
            "48000",
            "-movflags",
            "+faststart",
            "-t",
            f"{audio_duration:.3f}",
            str(out_path),
        ]
    )
    subprocess.run(cmd, check=True, capture_output=True, text=True)

    return RenderedVideo(
        draft_id=draft_id,
        output_path=out_path,
        duration_seconds=audio_duration,
        message=(
            f"Rendered {out_path.name} ({audio_duration:.1f}s, 1080×1920"
            f"{', Ken Burns ' + zoom_motion if use_motion else ''}). "
            f"Captions: ffmpeg ASS burn-in + captions.srt for YouTube."
        ),
    )
