"""Per-pack CapCut SFX guide — beat-timed from manifest + jumpscare plan."""

from __future__ import annotations

import json
from pathlib import Path


def _phase_for_index(i: int, total: int, *, has_jumpscare: bool) -> str:
    if i == 0:
        return "hook"
    if i == total - 1:
        return "finale" if has_jumpscare else "suspense_replay"
    if i >= total - 2 and total >= 6:
        return "false_calm"
    if i < max(2, total // 3):
        return "pattern"
    return "escalation"


_SFX_BY_PHASE: dict[str, dict[str, str]] = {
    "hook": {
        "job": "One diegetic wrong-detail cue — instant unease",
        "capcut_search": "notification / camera alert / glitch tick",
        "level": "40–50% · fade out 0.05s",
        "skip": "Risers, stingers, loud impacts",
    },
    "pattern": {
        "job": "Micro-cue per cut — grounds the anomaly",
        "capcut_search": "tap / ui click / lock / swipe",
        "level": "35–45% under VO",
        "skip": "Continuous drone beds",
    },
    "escalation": {
        "job": "Off-screen threat — acousmatic dread",
        "capcut_search": "footsteps / creak / static / muffled knock",
        "level": "35–50% · one cue per beat max",
        "skip": "Jump stingers mid-video",
    },
    "false_calm": {
        "job": "Strip layers — silence or room tone only (contrast for finale)",
        "capcut_search": "(none — delete SFX here)",
        "level": "Ambience ≤20% if any",
        "skip": "All risers and impacts",
    },
    "finale": {
        "job": "Fast-attack stinger synced ~2s before video end + optional thump on lunge",
        "capcut_search": "horror stinger / cinematic hit / impact",
        "level": "Stinger 85–100% · no fade-in · ≤0.3s peak",
        "skip": "Long noise/static layers",
    },
    "suspense_replay": {
        "job": "Hold tension — fade drone, no scare audio (replay bait)",
        "capcut_search": "(none) or very low room tone",
        "level": "Fade out last 2s · no stinger",
        "skip": "Jump sting entirely",
    },
}


def build_capcut_sfx_markdown(
    segments: list[dict],
    *,
    topic: str,
    jumpscare_plan: dict | None = None,
    audio_duration: float | None = None,
) -> str:
    """Build CAPCUT_SFX.md — per-segment SFX cues for CapCut timeline."""
    profile = (jumpscare_plan or {}).get("profile", "finale")
    has_js = (jumpscare_plan or {}).get("has_jumpscare", profile != "suspense_replay")
    total = len(segments)
    dur_note = f"{audio_duration:.1f}s" if audio_duration else "see voiceover.mp3"

    lines = [
        f"# CapCut SFX map — {topic}",
        "",
        f"**Audio length:** {dur_note} · **Profile:** `{profile}` · **Jumpscare:** {'yes' if has_js else 'no (suspense → replay)'}",
        "",
        "Full craft + sources: `data/research/HORROR_SOUND_EFFECTS_RESEARCH.md`",
        "CapCut steps: `channel/brand/capcut_horror_sfx.md`",
        "",
        "## Mix priorities",
        "",
        "1. VO loudest — SFX support, never mask hook",
        "2. Place SFX attack **1–3 frames before** each visual cut",
        "3. False calm = remove SFX layers",
        "4. Finale stinger only on `finale` profile (~2s before end)",
        "",
        "## Per-beat map",
        "",
        "| Start | Phase | Spoken | CapCut search | Level |",
        "|-------|-------|--------|---------------|-------|",
    ]

    for i, seg in enumerate(segments):
        phase = _phase_for_index(i, total, has_jumpscare=has_js)
        spec = _SFX_BY_PHASE[phase]
        start = float(seg.get("start_seconds", 0))
        spoken = str(seg.get("spoken_text", "")).replace("|", "/")[:50]
        lines.append(
            f"| {start:.1f}s | {phase} | {spoken} | {spec['capcut_search']} | {spec['level']} |"
        )

    lines.extend(
        [
            "",
            "## Phase notes",
            "",
        ]
    )
    for phase, spec in _SFX_BY_PHASE.items():
        lines.append(f"### {phase}")
        lines.append(f"- **Job:** {spec['job']}")
        lines.append(f"- **Skip:** {spec['skip']}")
        lines.append("")

    if has_js and audio_duration:
        sting_at = max(0.0, audio_duration - 2.5)
        lines.extend(
            [
                "## Finale stinger placement",
                "",
                f"- Target onset: **~{sting_at:.1f}s** ({audio_duration:.1f}s total − ~2.5s)",
                "- Align stinger attack with visual lunge cut in `clips/` finale segment",
                "- 🔊 Volume warning in YouTube title/description",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "## Suspense-replay ending",
                "",
                "- **No stinger** — let Shorts loop; end on unresolved hold",
                "- Skip 🔊 in title if pack uses suspense_replay profile",
                "",
            ]
        )

    lines.append("## Tracks in CapCut")
    lines.append("")
    lines.append("1. Video")
    lines.append("2. Voiceover (100%)")
    lines.append("3. SFX (this map)")
    lines.append("4. Music/ambience (optional, ducked under VO)")
    lines.append("")
    return "\n".join(lines)


def write_capcut_sfx_guide(pack_dir: Path) -> Path:
    """Generate CAPCUT_SFX.md from pack manifest.json."""
    manifest_path = pack_dir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"No manifest at {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    segments = manifest.get("segments") or []
    topic = manifest.get("topic") or "Don't Blink Short"
    plan = manifest.get("jumpscare_plan")

    audio_duration: float | None = None
    vo = pack_dir / "voiceover.mp3"
    if vo.exists():
        try:
            from shorts_bot.production.render_video import _probe_duration

            audio_duration = _probe_duration(vo)
        except Exception:
            audio_duration = None

    content = build_capcut_sfx_markdown(
        segments,
        topic=topic,
        jumpscare_plan=plan,
        audio_duration=audio_duration,
    )
    out = pack_dir / "CAPCUT_SFX.md"
    out.write_text(content, encoding="utf-8")
    return out
