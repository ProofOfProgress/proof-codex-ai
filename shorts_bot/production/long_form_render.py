"""Long-form video assembly — 16:9 blur pillarbox + stitch Shorts."""

from __future__ import annotations

import json
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

LANDSCAPE_WIDTH = 1920
LANDSCAPE_HEIGHT = 1080


@dataclass
class LandscapeSegment:
    draft_id: int
    source_path: Path
    landscape_path: Path
    duration_seconds: float
    hook: str = ""
    topic: str = ""


@dataclass
class CompilationRender:
    output_path: Path
    duration_seconds: float
    segments: list[LandscapeSegment]
    message: str


def probe_duration(video_path: Path) -> float:
    from shorts_bot.production.render_video import _probe_duration

    return _probe_duration(video_path)


def compose_vertical_in_landscape(
    input_path: Path,
    output_path: Path,
    *,
    width: int = LANDSCAPE_WIDTH,
    height: int = LANDSCAPE_HEIGHT,
    blur_strength: int = 20,
) -> Path:
    """Place 9:16 Short centered on blurred 16:9 background — captions stay visible."""
    if not input_path.is_file():
        raise FileNotFoundError(input_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    filter_complex = (
        f"[0:v]split=2[bg][fg];"
        f"[bg]scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},"
        f"boxblur=luma_radius={blur_strength}:luma_power=1:"
        f"chroma_radius={max(4, blur_strength // 2)}:chroma_power=1[blurred];"
        f"[fg]scale=-1:{height}:force_original_aspect_ratio=decrease[scaled];"
        f"[blurred][scaled]overlay=(W-w)/2:(H-h)/2[outv]"
    )
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(input_path),
            "-filter_complex",
            filter_complex,
            "-map",
            "[outv]",
            "-map",
            "0:a?",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "20",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            str(output_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return output_path


def _concat_segments(segment_paths: list[Path], output_path: Path) -> Path:
    if not segment_paths:
        raise ValueError("No segments to concat")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as tmp:
        list_path = Path(tmp.name)
        for seg in segment_paths:
            escaped = str(seg.resolve()).replace("'", "'\\''")
            tmp.write(f"file '{escaped}'\n")

    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(list_path),
                "-c",
                "copy",
                str(output_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(list_path),
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-crf",
                "20",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-movflags",
                "+faststart",
                str(output_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    finally:
        list_path.unlink(missing_ok=True)

    return output_path


def render_compilation(
    *,
    pack_dir: Path,
    segments: list[tuple[int, Path, str, str]],
    output_name: str = "final_long.mp4",
) -> CompilationRender:
    """Convert each Short to landscape, concat, write manifest segment metadata."""
    if len(segments) < 2:
        raise ValueError("Compilation needs at least 2 source Shorts")

    pack_dir.mkdir(parents=True, exist_ok=True)
    landscape_dir = pack_dir / "landscape_segments"
    landscape_dir.mkdir(exist_ok=True)

    rendered: list[LandscapeSegment] = []
    landscape_paths: list[Path] = []

    for draft_id, source, topic, hook in segments:
        if not source.is_file():
            raise FileNotFoundError(f"Draft #{draft_id} missing video: {source}")
        out_seg = landscape_dir / f"draft_{draft_id}_16x9.mp4"
        compose_vertical_in_landscape(source, out_seg)
        dur = probe_duration(out_seg)
        seg = LandscapeSegment(
            draft_id=draft_id,
            source_path=source,
            landscape_path=out_seg,
            duration_seconds=dur,
            hook=hook,
            topic=topic,
        )
        rendered.append(seg)
        landscape_paths.append(out_seg)

    output_path = pack_dir / output_name
    _concat_segments(landscape_paths, output_path)
    total = probe_duration(output_path)

    manifest = {
        "format": "long_compilation",
        "aspect_ratio": "16:9",
        "presentation": "blur_pillarbox",
        "output_video": output_name,
        "total_duration_seconds": round(total, 3),
        "segments": [
            {
                "draft_id": s.draft_id,
                "topic": s.topic,
                "hook": s.hook,
                "source_video": s.source_path.name,
                "landscape_video": s.landscape_path.name,
                "duration_seconds": round(s.duration_seconds, 3),
            }
            for s in rendered
        ],
    }
    (pack_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )

    return CompilationRender(
        output_path=output_path,
        duration_seconds=total,
        segments=rendered,
        message=f"Compiled {len(rendered)} Shorts → {output_path.name} ({total:.1f}s)",
    )
