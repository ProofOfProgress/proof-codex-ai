"""Timestamped video beat sheets — owner sees exactly what happens before Kling runs."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass

from shorts_bot.config import settings


@dataclass(frozen=True)
class BeatEntry:
    """One timed beat in the Short (~30s total)."""

    start_sec: float
    end_sec: float
    visual: str
    camera: str = ""
    audio_sfx: str = ""
    notes: str = ""


def _fmt_ts(seconds: float) -> str:
    s = max(0.0, float(seconds))
    m = int(s // 60)
    sec = s % 60
    return f"{m:01d}:{sec:05.2f}"


def format_beat_sheet_markdown(
    *,
    draft_id: int,
    topic: str,
    hook: str,
    beats: list[BeatEntry],
    rules: str = "",
) -> str:
    """Human-readable beat sheet for owner review before generation."""
    lines = [
        f"# Video beat sheet — draft #{draft_id}",
        "",
        f"**Topic:** {topic}",
        f"**Hook:** {hook}",
        "",
        "This is what will happen on screen, second by second, before we spend Kling credits.",
        "",
        "| Time | Visual | Camera | Sound (SFX only on launch) |",
        "|------|--------|--------|----------------------------|",
    ]
    for b in beats:
        cam = b.camera or "—"
        sfx = b.audio_sfx or "—"
        vis = b.visual.replace("|", "/").replace("\n", " ")
        note = f" ({b.notes})" if b.notes else ""
        lines.append(
            f"| {_fmt_ts(b.start_sec)}–{_fmt_ts(b.end_sec)} | {vis}{note} | {cam} | {sfx} |"
        )
    if rules.strip():
        lines.extend(["", "## Rules for this video", "", rules.strip()])
    lines.append("")
    return "\n".join(lines)


def beat_sheet_from_entries(raw: list[dict]) -> list[BeatEntry]:
    out: list[BeatEntry] = []
    for row in raw:
        if not isinstance(row, dict):
            continue
        try:
            out.append(
                BeatEntry(
                    start_sec=float(row.get("start_sec", 0)),
                    end_sec=float(row.get("end_sec", 0)),
                    visual=str(row.get("visual") or "").strip(),
                    camera=str(row.get("camera") or "").strip(),
                    audio_sfx=str(row.get("audio_sfx") or row.get("audio") or "").strip(),
                    notes=str(row.get("notes") or "").strip(),
                )
            )
        except (TypeError, ValueError):
            continue
    return [b for b in out if b.visual and b.end_sec > b.start_sec]


def load_beat_sheet(draft_id: int) -> list[BeatEntry]:
    from shorts_bot.drafts.meta import load_draft_meta

    raw = load_draft_meta(draft_id).get("beat_sheet") or []
    if isinstance(raw, list) and raw:
        return beat_sheet_from_entries(raw)
    return []


def save_beat_sheet(draft_id: int, beats: list[BeatEntry]) -> list[dict]:
    from shorts_bot.drafts.meta import save_draft_meta

    payload = [asdict(b) for b in beats]
    save_draft_meta(draft_id, beat_sheet=payload)
    return payload


def _sentences_from_text(text: str) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text.strip())
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", cleaned) if s.strip()]


def _dedupe_hook_prefix(hook: str, script: str) -> str:
    """Avoid turning an already-hook-led script into duplicate first beats."""
    h = re.sub(r"\s+", " ", hook.strip()).lower()
    s = re.sub(r"\s+", " ", script.strip())
    if h and s.lower().startswith(h):
        return s
    return f"{hook.strip()} {s}".strip()


def _sample_full_arc(sentences: list[str], *, max_beats: int = 9) -> list[str]:
    """Keep the hook, middle escalation, and final payoff when scripts are long."""
    if len(sentences) <= max_beats:
        return sentences
    count = max_beats
    last = len(sentences) - 1
    indexes: list[int] = []
    for i in range(count):
        idx = round(i * last / (count - 1))
        if idx not in indexes:
            indexes.append(idx)
    # Rounding can collapse adjacent points on short inputs; fill deterministically.
    cursor = 0
    while len(indexes) < count and cursor <= last:
        if cursor not in indexes:
            indexes.append(cursor)
        cursor += 1
    indexes = sorted(indexes[:count])
    if indexes[-1] != last:
        indexes[-1] = last
    return [sentences[i] for i in indexes]


def _significant_words(text: str) -> set[str]:
    stop = {
        "about",
        "after",
        "again",
        "always",
        "before",
        "could",
        "there",
        "their",
        "these",
        "those",
        "until",
        "where",
        "which",
        "would",
        "you",
        "your",
    }
    return {
        w
        for w in re.findall(r"[a-z0-9']+", text.lower())
        if len(w) >= 4 and w not in stop
    }


def _missing_script_payoff(beats: list[BeatEntry], script: str) -> bool:
    sentences = _sentences_from_text(script)
    if not beats or not sentences:
        return False
    final_words = _significant_words(" ".join(sentences[-2:]))
    if not final_words:
        return False
    beat_words = _significant_words(" ".join(b.visual for b in beats[-3:]))
    overlap = final_words & beat_words
    needed = 1 if len(final_words) <= 3 else 2
    return len(overlap) < needed


def write_beat_sheet_files(
    pack_dir,
    *,
    draft_id: int,
    topic: str,
    hook: str,
    beats: list[BeatEntry],
    rules: str = "",
) -> None:
    """Write beat sheet into production pack before expensive video gen."""
    from pathlib import Path

    root = Path(pack_dir)
    root.mkdir(parents=True, exist_ok=True)
    md = format_beat_sheet_markdown(
        draft_id=draft_id, topic=topic, hook=hook, beats=beats, rules=rules
    )
    (root / "VIDEO_BEAT_SHEET.md").write_text(md, encoding="utf-8")
    (root / "beat_sheet.json").write_text(
        json.dumps([asdict(b) for b in beats], indent=2), encoding="utf-8"
    )


def beats_for_kling_clip(
    beats: list[BeatEntry],
    clip_index: int,
    *,
    clip_seconds: int,
    clips_per_short: int,
) -> list[dict]:
    """Slice beat sheet into one Kling clip window → multi_prompt shots."""
    if not beats:
        return []
    total = clip_seconds * clips_per_short
    clip_start = clip_index * clip_seconds
    clip_end = clip_start + clip_seconds
    in_clip = [b for b in beats if b.start_sec < clip_end and b.end_sec > clip_start]
    if not in_clip:
        return []
    shots: list[dict] = []
    for b in in_clip:
        local_start = max(0.0, b.start_sec - clip_start)
        local_end = min(float(clip_seconds), b.end_sec - clip_start)
        dur = max(1, int(round(local_end - local_start)))
        prompt = b.visual
        if b.camera:
            prompt = f"{prompt}. Camera: {b.camera}"
        shots.append({"prompt": prompt, "duration": dur})
    # Normalize durations to clip_seconds
    if shots:
        total_d = sum(s["duration"] for s in shots)
        if total_d != clip_seconds and total_d > 0:
            scale = clip_seconds / total_d
            for s in shots:
                s["duration"] = max(1, int(round(s["duration"] * scale)))
            drift = clip_seconds - sum(s["duration"] for s in shots)
            shots[-1]["duration"] = max(1, shots[-1]["duration"] + drift)
    return shots


def launch_rules_blurb(draft_id: int | None) -> str:
    from shorts_bot.production.launch_phase import is_silent_launch_draft

    if is_silent_launch_draft(draft_id):
        return (
            "- **No talking, no subtitles** (launch videos 1–3)\n"
            "- **SFX on:** wind, flicker buzz, footsteps, creaks, horror sting\n"
            "- **720p** cinematic motion — never a static slideshow\n"
            "- **Form 2** rural anomaly when script calls for escalation"
        )
    return "- Character dialogue + burned-in subtitles after launch phase"


def default_beat_sheet_for_draft(
    *,
    draft_id: int,
    topic: str,
    hook: str,
    script: str,
    total_seconds: float | None = None,
    visual_beats: list[str] | None = None,
) -> list[BeatEntry]:
    """Build ~30s beat sheet from hook + script when LLM did not supply one."""
    dur = total_seconds or (
        settings.kling_clip_seconds * settings.kling_clips_per_short
    )
    visual_arc = [str(v).strip() for v in (visual_beats or []) if str(v).strip()]
    text = _dedupe_hook_prefix(hook, script)
    sentences = _sample_full_arc(_sentences_from_text(text))
    if visual_arc:
        sentences = visual_arc
    if not sentences:
        sentences = [text or hook or topic]
    n = min(9, max(6, len(sentences)))
    step = dur / n
    beats: list[BeatEntry] = []
    for i in range(n):
        start = i * step
        end = dur if i == n - 1 else (i + 1) * step
        sent = sentences[min(i, len(sentences) - 1)]
        beats.append(
            BeatEntry(
                start_sec=round(start, 2),
                end_sec=round(end, 2),
                visual=sent,
                camera="Handheld POV, constant motion",
                audio_sfx="wind + flicker" if i % 2 == 0 else "footstep / creak",
            )
        )
    return beats


def ensure_beat_sheet(
    draft_id: int,
    *,
    topic: str,
    hook: str,
    script: str,
) -> list[BeatEntry]:
    """Load saved beat sheet or build default."""
    from shorts_bot.drafts.meta import load_draft_meta

    meta = load_draft_meta(draft_id)
    visual_arc = [str(v).strip() for v in (meta.get("visual_beats") or []) if str(v).strip()]
    existing = load_beat_sheet(draft_id)
    existing_visuals = [b.visual for b in existing]
    if existing and (
        meta.get("beat_sheet_approved")
        or (visual_arc and existing_visuals == visual_arc)
        or not _missing_script_payoff(existing, script)
    ):
        return existing
    beats = default_beat_sheet_for_draft(
        draft_id=draft_id,
        topic=topic,
        hook=hook,
        script=script,
        visual_beats=visual_arc or None,
    )
    save_beat_sheet(draft_id, beats)
    return beats
