"""Programmatic horror SFX — ffmpeg lavfi cues synced to manifest beats."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from shorts_bot.production.capcut_sfx import _phase_for_index
from shorts_bot.production.jumpscare_timing import JumpscarePlan, sting_start_seconds


@dataclass(frozen=True)
class SfxCue:
    start_seconds: float
    kind: str
    gain: float = 1.0


def _lavfi_for_kind(kind: str, *, duration_hint: float = 0.2) -> str:
    """One-shot SFX generator (48 kHz). Fast attack on stinger — no long static."""
    d = max(0.05, min(duration_hint, 0.35))
    if kind == "cam_alert":
        return (
            "aevalsrc='0.45*sin(880*2*PI*t)*exp(-t*18)+0.35*sin(660*2*PI*(t-0.08))*"
            "if(gte(t,0.08),exp(-(t-0.08)*22),0)':d=0.22:sample_rate=48000"
        )
    if kind == "ui_tap":
        return (
            f"anoisesrc=color=white:duration={d:.3f}:sample_rate=48000,"
            "highpass=f=2500,lowpass=f=9000,volume=0.35,"
            "afade=t=in:st=0:d=0.005,afade=t=out:st=0.03:d=0.02"
        )
    if kind == "footstep":
        return (
            f"aevalsrc='0.55*sin(55*2*PI*t)*exp(-t*35)':d={min(d, 0.12):.3f}:sample_rate=48000"
        )
    if kind == "creak":
        return (
            f"anoisesrc=color=white:duration={min(d, 0.28):.3f}:sample_rate=48000,"
            "lowpass=f=450,highpass=f=80,volume=0.4,"
            "afade=t=in:st=0:d=0.02,afade=t=out:st=0.18:d=0.08"
        )
    if kind == "speaker_tap":
        return (
            "aevalsrc='0.5*sin(180*2*PI*t)*exp(-t*40)':d=0.09:sample_rate=48000"
        )
    if kind == "static_burst":
        return (
            f"anoisesrc=color=white:duration={min(d, 0.15):.3f}:sample_rate=48000,"
            "bandpass=f=1200:w=800,volume=0.35,afade=t=out:st=0.05:d=0.06"
        )
    if kind == "stinger":
        return (
            "aevalsrc='if(lt(t,0.015),0.95*sin(440*2*PI*t)*exp(-t*65),"
            "if(lt(t,0.11),0.8*sin(90*2*PI*t)*exp(-(t-0.015)*28),0))':d=0.25:sample_rate=48000"
        )
    if kind == "stinger_noise":
        return (
            "anoisesrc=color=white:duration=0.14:sample_rate=48000,"
            "highpass=f=1800,lowpass=f=7500,volume=0.55,"
            "afade=t=in:st=0:d=0.003,afade=t=out:st=0.08:d=0.05"
        )
    return (
        f"anoisesrc=color=white:duration={d:.3f}:sample_rate=48000,"
        "highpass=f=1500,volume=0.2,afade=t=out:st=0.02:d=0.04"
    )


_PHASE_KIND: dict[str, str | None] = {
    "hook": "cam_alert",
    "pattern": "ui_tap",
    "escalation": "creak",
    "false_calm": None,
    "finale": None,
    "suspense_replay": None,
}


def build_sfx_cues(
    segments: list[dict],
    plan: JumpscarePlan,
    *,
    audio_duration: float,
) -> list[SfxCue]:
    """Map manifest segments → timed SFX cues (research-backed beat map)."""
    total = len(segments)
    has_js = plan.has_jumpscare
    cues: list[SfxCue] = []

    for i, seg in enumerate(segments):
        phase = _phase_for_index(i, total, has_jumpscare=has_js)
        kind = _PHASE_KIND.get(phase)
        if not kind:
            continue
        if phase == "escalation" and i % 2 == 0:
            kind = "footstep"
        if phase == "hook":
            kind = "cam_alert"
        start = float(seg.get("start_seconds", 0))
        # Lead visual by ~2 frames
        start = max(0.0, start - 0.05)
        gain = 0.55 if phase == "hook" else 0.42
        cues.append(SfxCue(start_seconds=start, kind=kind, gain=gain))

    if has_js:
        sting_at = sting_start_seconds(plan, segments=segments, total_duration=audio_duration)
        if sting_at is None:
            sting_at = max(0.0, audio_duration - 2.5)
        cues.append(SfxCue(start_seconds=sting_at, kind="stinger", gain=1.0))
        cues.append(SfxCue(start_seconds=sting_at + 0.01, kind="stinger_noise", gain=0.85))

    return cues


def mix_horror_sfx_into_voiceover(
    voiceover_path: Path,
    cues: list[SfxCue],
    *,
    output_path: Path | None = None,
) -> Path:
    """Layer procedural SFX on VO; returns path to mixed MP3."""
    if not cues:
        return voiceover_path

    out = output_path or voiceover_path.parent / "_voiceover_sfx.mp3"
    delay_ms = [int(c.start_seconds * 1000) for c in cues]
    inputs = ["-i", str(voiceover_path)]
    filter_parts: list[str] = []

    for i, cue in enumerate(cues):
        lavfi = _lavfi_for_kind(cue.kind)
        inputs.extend(["-f", "lavfi", "-i", lavfi])
        idx = i + 1
        ms = delay_ms[i]
        vol = cue.gain
        filter_parts.append(
            f"[{idx}:a]adelay={ms}|{ms},volume={vol:.3f}[s{idx}]"
        )

    mix_inputs = "[0:a]" + "".join(f"[s{i+1}]" for i in range(len(cues)))
    n = len(cues) + 1
    filter_parts.append(
        f"{mix_inputs}amix=inputs={n}:duration=first:dropout_transition=0:normalize=0[out]"
    )
    filter_complex = ";".join(filter_parts)

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            *inputs,
            "-filter_complex",
            filter_complex,
            "-map",
            "[out]",
            "-c:a",
            "libmp3lame",
            "-b:a",
            "192k",
            str(out),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return out


def apply_horror_sfx_to_pack_audio(
    pack_dir: Path,
    segments: list[dict],
    plan: JumpscarePlan,
    voiceover_path: Path,
    *,
    audio_duration: float,
) -> Path:
    """Build cues from segments + plan, mix into VO."""
    cues = build_sfx_cues(segments, plan, audio_duration=audio_duration)
    (pack_dir / "sfx_cues.json").write_text(
        __import__("json").dumps(
            [{"start": c.start_seconds, "kind": c.kind, "gain": c.gain} for c in cues],
            indent=2,
        ),
        encoding="utf-8",
    )
    return mix_horror_sfx_into_voiceover(voiceover_path, cues)
