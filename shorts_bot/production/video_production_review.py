"""Gemini production review — full Short critique (AV sync, jumpscare, captions, frames)."""

from __future__ import annotations

import base64
import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from shorts_bot.config import settings


@dataclass
class ProductionReview:
    score: float
    concept_score: float
    production_score: float
    summary: str
    av_sync: str
    jumpscare: str
    captions: str
    visuals: str
    weird_frames: list[str] = field(default_factory=list)
    fixes: list[str] = field(default_factory=list)
    frame_times: list[float] = field(default_factory=list)
    frame_paths: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)
    # Deep review fields (empty on shallow review)
    vo_visual_match: str = ""
    subtitle_sync: str = ""
    visual_glitches: list[str] = field(default_factory=list)
    framing_issues: list[str] = field(default_factory=list)
    nonsensical_elements: list[str] = field(default_factory=list)
    things_that_shouldnt_be_there: list[str] = field(default_factory=list)
    review_mode: str = "standard"

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "concept_score": self.concept_score,
            "production_score": self.production_score,
            "summary": self.summary,
            "av_sync": self.av_sync,
            "jumpscare": self.jumpscare,
            "captions": self.captions,
            "visuals": self.visuals,
            "weird_frames": self.weird_frames,
            "fixes": self.fixes,
            "frame_times": self.frame_times,
            "frame_paths": self.frame_paths,
            "raw": self.raw,
            "vo_visual_match": self.vo_visual_match,
            "subtitle_sync": self.subtitle_sync,
            "visual_glitches": self.visual_glitches,
            "framing_issues": self.framing_issues,
            "nonsensical_elements": self.nonsensical_elements,
            "things_that_shouldnt_be_there": self.things_that_shouldnt_be_there,
            "review_mode": self.review_mode,
        }


def _report_path(pack_dir: Path, *, deep: bool = False) -> Path:
    return pack_dir / ("gemini_deep_review.json" if deep else "gemini_review.json")


def _load_caption_timeline(pack_dir: Path) -> list[dict]:
    path = pack_dir / "caption_segments.json"
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _caption_at_time(captions: list[dict], t: float) -> str:
    for row in captions:
        if float(row.get("start_seconds", 0)) <= t < float(row.get("end_seconds", 0)):
            return str(row.get("spoken_text", ""))[:120]
    return ""


def pick_deep_frame_times(
    duration: float,
    pack_dir: Path,
    *,
    max_frames: int = 14,
) -> list[float]:
    """Every visual cut + caption midpoints + finale — dense production audit."""
    manifest = _load_manifest(pack_dir)
    segments = manifest.get("segments") or []
    captions = _load_caption_timeline(pack_dir)
    first_start = float(segments[0].get("start_seconds", 0)) if segments else 0.0
    last_end = float(segments[-1].get("end_seconds", duration)) if segments else duration
    span = max(0.01, last_end - first_start)
    scale = duration / span
    cap = max(0.2, duration - 0.2)

    picks: list[float] = [0.35]
    for seg in segments:
        s0 = float(seg.get("start_seconds", 0)) - first_start
        t = min(cap, max(0.2, s0 * scale + 0.12))
        picks.append(round(t, 2))
    for row in captions:
        s0 = float(row.get("start_seconds", 0))
        s1 = float(row.get("end_seconds", s0))
        mid = min(cap, (s0 + s1) / 2)
        if mid > 0.3:
            picks.append(round(mid, 2))
    picks.append(min(cap, duration - 0.15))

    deduped: list[float] = []
    for t in sorted(picks):
        if not deduped or abs(t - deduped[-1]) >= 0.38:
            deduped.append(t)
    return deduped[:max_frames]


def _probe_duration(video_path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(video_path),
        ],
        text=True,
    )
    return float(out.strip())


def _load_manifest(pack_dir: Path) -> dict[str, Any]:
    path = pack_dir / "manifest.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def pick_production_frame_times(
    duration: float,
    pack_dir: Path,
    *,
    max_frames: int = 10,
) -> list[float]:
    """Hook, segment cuts, and finale (start + flash + end) — finale always included."""
    manifest = _load_manifest(pack_dir)
    segments = manifest.get("segments") or []
    first_start = float(segments[0].get("start_seconds", 0)) if segments else 0.0
    last_end = float(segments[-1].get("end_seconds", duration)) if segments else duration
    span = max(0.01, last_end - first_start)
    scale = duration / span
    cap = max(0.2, duration - 0.25)

    must_have: list[float] = [0.5]
    mid: list[float] = []
    finale: list[float] = []

    for i, seg in enumerate(segments):
        s0 = float(seg.get("start_seconds", 0)) - first_start
        t = min(max(0.2, s0 * scale + 0.15), cap)
        if i == len(segments) - 1:
            finale.append(t)
            s1 = float(seg.get("end_seconds", last_end)) - first_start
            finale.append(min(cap, (s1 * scale) - 0.35))
            finale.append(min(cap, duration - 0.15))
        else:
            mid.append(t)

    picked: list[float] = list(must_have)
    budget = max_frames - len(must_have) - len(finale)
    for t in sorted(mid):
        t = min(max(0.15, t), cap)
        if budget <= 0:
            break
        if not picked or abs(t - picked[-1]) >= 0.55:
            picked.append(round(t, 2))
            budget -= 1
    for t in sorted(finale):
        t = min(max(0.15, t), cap)
        if not picked or abs(t - picked[-1]) >= 0.45:
            picked.append(round(t, 2))
    return sorted(set(picked))[:max_frames]


def _extract_frame(video_path: Path, t: float, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    width = settings.vision_qc_frame_width
    quality = settings.vision_qc_jpeg_quality
    qv = str(max(2, min(31, int((100 - quality) / 3))))
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-ss",
            f"{t:.3f}",
            "-i",
            str(video_path),
            "-frames:v",
            "1",
            "-vf",
            f"scale={width}:-2",
            "-q:v",
            qv,
            str(out_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def _parse_json(raw: str) -> dict[str, Any]:
    text = raw.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    if fence:
        text = fence.group(1)
    else:
        brace = re.search(r"\{.*\}", text, re.S)
        if brace:
            text = brace.group(0)
    return json.loads(text)


def _format_caption_context(captions: list[dict], frame_times: list[float]) -> str:
    if not captions:
        return "Caption timeline: not available."
    lines = ["Caption timeline (voice-synced, floats on video):"]
    for row in captions[:24]:
        s0 = float(row.get("start_seconds", 0))
        s1 = float(row.get("end_seconds", s0))
        text = str(row.get("spoken_text", ""))[:80]
        lines.append(f"  {s0:.1f}s–{s1:.1f}s: {text}")
    lines.append("Per-frame caption visible:")
    for t in frame_times:
        cap = _caption_at_time(captions, t)
        if cap:
            lines.append(f"  @{t:.1f}s: «{cap}»")
    return "\n".join(lines)


def _gemini_review(
    frames: list[tuple[float, Path]],
    *,
    topic: str,
    hook: str,
    script: str,
    sfx_cues: list[dict],
    captions: list[dict] | None = None,
    deep: bool = False,
) -> dict[str, Any]:
    from shorts_bot.llm.provider import get_llm_backend

    backend = get_llm_backend()
    if backend is None or backend.provider != "gemini":
        raise RuntimeError("Gemini API key required for production review")

    model = (settings.gemini_vision_model or settings.gemini_model).strip()
    labels = ", ".join(f"{t:.1f}s" for t, _ in frames)
    sting = next((c for c in sfx_cues if c.get("kind") == "stinger"), None)
    sting_note = f"Audio stinger cue at {sting['start']:.1f}s" if sting else "No stinger cue logged"

    cap_ctx = _format_caption_context(captions or [], [t for t, _ in frames])
    if deep:
        prompt = (
            "You are a senior YouTube Shorts post-production QC lead auditing a horror Short.\n"
            f"Frames in order at: {labels}. Each frame is a screenshot from the FINAL rendered MP4 "
            "(with burned-in captions and composited phone/CCTV UI).\n\n"
            f"Topic: {topic[:120]}\nHook: {hook[:120]}\n"
            f"Full VO script: {script[:900]}\n{sting_note}\n\n{cap_ctx}\n\n"
            "Deep audit PRODUCTION QUALITY ONLY. Be brutally specific with timestamps.\n"
            "1) VO vs VIDEO — does the image shown match what the narrator is saying at that moment? "
            "Flag every cut where visual scene is wrong for the spoken line.\n"
            "2) SUBTITLES vs VO vs VIDEO — do burned-in captions match the script words AND stay on "
            "screen long enough? Do captions change while the same line is still being spoken? "
            "Caption vs visual independence issues?\n"
            "3) VISUAL GLITCHES — compression artifacts, frozen frames, sudden jumps, AI morphing, "
            "duplicate limbs, face distortions, screen tearing, overlay misalignment.\n"
            "4) THINGS THAT SHOULDN'T BE THERE — cosy aesthetic, daylight cheer, readable AI gibberish "
            "text, watermarks, wrong objects, anachronisms, duplicate UI layers.\n"
            "5) FRAMING — subject cropped badly, captions in Shorts UI dead zone, empty dead space, "
            "phone UI off-center, subject behind caption bar.\n"
            "6) NONSENSICAL ELEMENTS — story logic breaks visible on screen (empty hallway then figure "
            "with no transition sense, wrong room, etc).\n"
            "7) JUMPSCARE — visible lunge motion vs audio sting timing.\n\n"
            "Return ONLY JSON. All score fields are integers 0-100 (not 1-10): "
            "score, concept_score, production_score, jumpscare, captions, visuals, "
            "vo_visual_match, subtitle_sync, summary, av_sync, "
            "visual_glitches (string[]), framing_issues (string[]), "
            "things_that_shouldnt_be_there (string[]), nonsensical_elements (string[]), "
            "weird_frames (string[]), fixes (string[])."
        )
    else:
        prompt = (
            "You are a horror YouTube Shorts producer reviewing a near-finished Don't Blink draft.\n"
            f"Frames in order at: {labels}.\n"
            f"Topic: {topic[:120]}\nHook: {hook[:120]}\n"
            f"Approved script (caption text should match this, not ASR errors): {script[:500]}\n"
            f"{sting_note}\n\n{cap_ctx}\n\n"
            "Critique PRODUCTION only (concept is close). Focus on:\n"
            "1) AV sync — do cuts match VO beats? Any late/early visuals?\n"
            "2) Jumpscare — is there a visible finale lunge/zoom/flash synced with audio sting? "
            "Or is scare audio-only / mistimed?\n"
            "3) Captions — typos, timing vs voice, safe zone?\n"
            "4) Weird frames — AI wrongness, gibberish text, wrong setting.\n"
            "5) Top 5 concrete pipeline fixes.\n\n"
            "Return ONLY JSON keys: score (1-10 overall), concept_score (1-10), production_score (1-10), "
            "summary (string), av_sync (string), jumpscare (string), captions (string), visuals (string), "
            "weird_frames (string[]), fixes (string[])."
        )

    content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
    for _t, path in frames:
        b64 = base64.standard_b64encode(path.read_bytes()).decode("ascii")
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
            }
        )

    resp = backend.client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": content}],
        max_tokens=2400 if deep else 1200,
        temperature=0.2,
    )
    raw = (resp.choices[0].message.content or "").strip()
    try:
        return _parse_json(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Gemini returned non-JSON: {raw[:400]}") from exc


def _parse_score_field(val: Any) -> float:
    """Normalize Gemini scores to 0-100."""
    if isinstance(val, (int, float)):
        v = float(val)
    else:
        m = re.search(r"([\d.]+)", str(val))
        v = float(m.group(1)) if m else 0.0
    if 0 < v <= 10:
        return v * 10.0
    return v


def _review_from_data(
    data: dict[str, Any],
    *,
    times: list[float],
    frames: list[tuple[float, Path]],
    deep: bool,
) -> ProductionReview:
    return ProductionReview(
        score=_parse_score_field(data.get("score", 0)),
        concept_score=_parse_score_field(data.get("concept_score", 0)),
        production_score=_parse_score_field(data.get("production_score", 0)),
        summary=str(data.get("summary", "")),
        av_sync=str(data.get("av_sync", "")),
        jumpscare=str(_parse_score_field(data.get("jumpscare", 0))),
        captions=str(_parse_score_field(data.get("captions", 0))),
        visuals=str(_parse_score_field(data.get("visuals", 0))),
        weird_frames=[str(x) for x in (data.get("weird_frames") or [])],
        fixes=[str(x) for x in (data.get("fixes") or [])],
        frame_times=times,
        frame_paths=[str(p) for _, p in frames],
        raw=data,
        vo_visual_match=str(data.get("vo_visual_match", "")),
        subtitle_sync=str(data.get("subtitle_sync", "")),
        visual_glitches=[str(x) for x in (data.get("visual_glitches") or [])],
        framing_issues=[str(x) for x in (data.get("framing_issues") or [])],
        nonsensical_elements=[str(x) for x in (data.get("nonsensical_elements") or [])],
        things_that_shouldnt_be_there=[
            str(x) for x in (data.get("things_that_shouldnt_be_there") or [])
        ],
        review_mode="deep" if deep else "standard",
    )


def run_production_review(
    video_path: Path,
    pack_dir: Path,
    *,
    use_cache: bool = False,
    deep: bool = False,
) -> ProductionReview:
    """Extract beat-aware frames and get Gemini production feedback."""
    if not video_path.exists():
        raise FileNotFoundError(video_path)

    report_path = _report_path(pack_dir, deep=deep)
    if use_cache and report_path.exists():
        try:
            cached = json.loads(report_path.read_text(encoding="utf-8"))
            if float(cached.get("video_mtime", 0)) == video_path.stat().st_mtime:
                fields = {k: cached[k] for k in ProductionReview.__dataclass_fields__ if k in cached}
                return ProductionReview(**fields)
        except (json.JSONDecodeError, OSError, TypeError):
            pass

    manifest = _load_manifest(pack_dir)
    topic = str(manifest.get("topic") or "")
    hook = str(manifest.get("hook") or "")
    script = str(manifest.get("script") or "")

    sfx_path = pack_dir / "sfx_cues.json"
    sfx_cues: list[dict] = []
    if sfx_path.exists():
        sfx_cues = json.loads(sfx_path.read_text(encoding="utf-8"))

    captions = _load_caption_timeline(pack_dir)
    duration = _probe_duration(video_path)
    if deep:
        times = pick_deep_frame_times(duration, pack_dir, max_frames=14)
    else:
        times = pick_production_frame_times(duration, pack_dir, max_frames=10)
    frames_dir = pack_dir / "review_frames"
    frames: list[tuple[float, Path]] = []
    for i, t in enumerate(times):
        path = frames_dir / f"review_{i:02d}_{t:.1f}s.jpg"
        try:
            _extract_frame(video_path, t, path)
        except subprocess.CalledProcessError:
            continue
        if path.exists() and path.stat().st_size > 400:
            frames.append((t, path))
    if not frames:
        raise RuntimeError("No review frames extracted from video")

    data = _gemini_review(
        frames,
        topic=topic,
        hook=hook,
        script=script,
        sfx_cues=sfx_cues,
        captions=captions,
        deep=deep,
    )

    review = _review_from_data(data, times=times, frames=frames, deep=deep)

    payload = review.to_dict()
    payload["video_mtime"] = video_path.stat().st_mtime
    report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return review
