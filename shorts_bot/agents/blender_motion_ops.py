"""AlphaBeta001 / agent ops — English motion → Blender keyframes → cloud render.

Owner PC never runs Blender. All work happens on the cloud VM.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from shorts_bot.config import settings

PHASES = ("open", "wave", "lunge")


def pack_dir(draft_id: int) -> Path:
    return settings.data_dir / "production" / f"draft_{draft_id}"


def move_creature_from_prompt(
    draft_id: int,
    prompt: str,
    *,
    phase: str = "wave",
    force: bool = True,
) -> dict:
    """Turn English into motion_{phase}.json — Gemini when key set, else procedural."""
    from shorts_bot.production.blender.motion_prompt import (
        generate_motion_keyframes,
        load_beat_prompt,
        motion_cache_path,
        resolve_backend,
    )

    phase = phase if phase in PHASES else "wave"
    text = (prompt or "").strip() or load_beat_prompt(draft_id, phase)
    payload = generate_motion_keyframes(text, phase=phase)
    out = motion_cache_path(pack_dir(draft_id), phase)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return {
        "ok": True,
        "draft_id": draft_id,
        "phase": phase,
        "prompt": text[:500],
        "backend": payload.get("backend", resolve_backend()),
        "keyframes": len(payload.get("keyframes") or []),
        "motion_file": str(out),
        "message": (
            f"Motion saved for draft #{draft_id} ({phase}): {out.name} "
            f"via {payload.get('backend')} — {len(payload.get('keyframes') or [])} keyframes."
        ),
    }


def render_blender_preview(
    draft_id: int,
    *,
    phase: str = "wave",
    samples: int | None = None,
) -> dict:
    """Single clip PNG still — fast sanity check (~8 min cloud render)."""
    from shorts_bot.production.blender.motion_prompt import prepare_motion_for_pack

    pack = pack_dir(draft_id)
    prepare_motion_for_pack(pack, draft_id, phases=(phase,), force=True)
    samp = samples or settings.blender_samples
    out_png = pack / f"blender_preview_{phase}.png"
    script = (
        Path(__file__).resolve().parent.parent
        / "production"
        / "blender"
        / "build_and_render.py"
    )
    cmd = [
        "blender", "--background", "--python", str(script),
        "--", "--draft-id", str(draft_id),
        "--pack-dir", str(pack),
        "--preview", "--phase", phase,
        "--samples", str(samp),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "")[-1500:]
        return {"ok": False, "message": f"Blender preview failed:\n{tail}"}
    return {
        "ok": True,
        "draft_id": draft_id,
        "phase": phase,
        "preview_png": str(out_png),
        "watch_url": f"http://127.0.0.1:8080/preview/draft/{draft_id}",
        "message": f"Preview PNG: {out_png}. Open in Cursor file tree or /preview/draft/{draft_id}",
    }


def start_blender_render_background(draft_id: int, *, force: bool = True) -> dict:
    """Full 30s Short — cloud tmux job (~30–45 min). Owner PC does nothing."""
    pack = pack_dir(draft_id)
    log = pack / "render_log.txt"
    session = f"blender-draft-{draft_id}"
    cmd = (
        f'tmux -f /exec-daemon/tmux.portal.conf kill-session -t "={session}" 2>/dev/null; '
        f'tmux -f /exec-daemon/tmux.portal.conf new-session -d -s "{session}" -c "/workspace" '
        f'-- bash -lc "python3 -m shorts_bot.production.blender.produce_cli --draft-id {draft_id}'
        f'{" --force" if force else ""} 2>&1 | tee {log}"'
    )
    subprocess.run(["bash", "-lc", cmd], check=False)
    return {
        "ok": True,
        "draft_id": draft_id,
        "session": session,
        "log_file": str(log),
        "watch_url": f"http://127.0.0.1:8080/preview/draft/{draft_id}",
        "message": (
            f"Blender render started on cloud for draft #{draft_id} (~30–45 min). "
            f"Your PC does nothing. When done, open preview/draft/{draft_id} or "
            f"{pack}/preview_frames/full_contact_sheet.png"
        ),
    }


def try_parse_and_run(message: str) -> str | None:
    """If message is a blender motion/render command, run it and return reply text."""
    from shorts_bot.services.chat_router import parse_blender_motion_request, parse_blender_render_request

    motion = parse_blender_motion_request(message)
    if motion:
        r = move_creature_from_prompt(
            motion["draft_id"],
            motion["prompt"],
            phase=motion["phase"],
        )
        return r["message"]

    render = parse_blender_render_request(message)
    if render:
        if render.get("preview"):
            r = render_blender_preview(render["draft_id"], phase=render.get("phase", "wave"))
        elif render.get("background"):
            r = start_blender_render_background(render["draft_id"], force=render.get("force", True))
        else:
            r = start_blender_render_background(render["draft_id"], force=True)
        return r.get("message", str(r))

    return None
