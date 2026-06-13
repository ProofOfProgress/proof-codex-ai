"""Generate data/OPS_STATUS.md — launch ops snapshot for cloud agents."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from shorts_bot.compliance.upload_guard import check_upload_allowed
from shorts_bot.config import settings
from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.memory.store import MemoryStore
from shorts_bot.production.queue_cli import _pack_dir, list_approved, next_draft_id
from shorts_bot.youtube.google_auth import auth_status


def _clip_count(draft_id: int) -> int:
    clips = _pack_dir(draft_id) / "clips"
    if not clips.is_dir():
        return 0
    return len([p for p in clips.glob("*.mp4") if p.stat().st_size > 10_000])


def _has_final(draft_id: int) -> bool:
    p = _pack_dir(draft_id) / "final_short.mp4"
    return p.exists() and p.stat().st_size > 50_000


def _live_video() -> dict | None:
    path = settings.data_dir / "production" / "draft_2" / "upload_result.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def build_ops_status_markdown() -> str:
    store = MemoryStore(settings.database_path)
    memory = MemoryExtensions(store)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "# Don't Blink — ops status",
        "",
        f"_Generated {now}_",
        "",
        "## Video #1 (LIVE)",
    ]
    live = _live_video()
    if live and live.get("video_id"):
        vid = live["video_id"]
        lines.append(f"- **URL:** https://youtube.com/shorts/{vid}")
        lines.append(f"- **Draft:** #2 — mirror blink horror")
    else:
        lines.append("- Draft #2 — check `data/production/draft_2/upload_result.json`")

    lines.extend(["", "## Production queue (approved)"])
    for d in list_approved(store):
        clips = _clip_count(d.id)
        final = "✓ final_short.mp4" if _has_final(d.id) else f"{clips} I2V clips"
        meta = "✓" if (_pack_dir(d.id) / "UPLOAD_READY.md").exists() else "—"
        lines.append(f"- **#{d.id}** {d.topic[:56]} — {final}; upload meta {meta}")

    nid = next_draft_id(store)
    lines.extend(
        [
            "",
            "## Next action",
            f"- **Run pipeline:** `python3 -m shorts_bot.production.queue_cli --run-next --no-upload`"
            + (f" (draft #{nid})" if nid else " — queue complete"),
            "- **Sequential only** — one Replicate I2V job at a time (429 avoidance)",
            "",
            "## Upload guard",
        ]
    )

    sample = None
    if nid:
        sample = store.get_draft(nid)
    else:
        approved = list_approved(store)
        if approved:
            sample = approved[0]
    if sample:
        report = check_upload_allowed(
            store,
            memory,
            draft_id=sample.id,
            topic=sample.topic,
            hook=sample.hook,
            script=sample.script,
            title=sample.hook,
        )
        if report.allowed:
            lines.append("- **Clear** — next upload allowed")
        else:
            lines.append("- **Blocked:** " + "; ".join(report.issues))
        if report.warnings:
            lines.append("- Warnings: " + "; ".join(report.warnings))
        recent = memory.recent_uploads(hours=48)
        if recent:
            last = recent[0]
            last_at = datetime.fromisoformat(str(last["uploaded_at"]).replace("Z", "+00:00"))
            hours_ago = (datetime.now(timezone.utc) - last_at).total_seconds() / 3600
            wait = max(0.0, float(settings.min_hours_between_uploads) - hours_ago)
            lines.append(
                f"- Last valid upload: draft #{last.get('draft_id')} "
                f"({hours_ago:.1f}h ago) — ~{wait:.1f}h until cooldown clear"
            )
    else:
        lines.append("- No draft sample for guard check")

    yt = auth_status()
    lines.extend(
        [
            "",
            "## YouTube auth",
            f"- Credentials: {'✓' if yt.get('credentials_configured') else '—'}",
            f"- OAuth token: {'✓' if yt.get('token_saved') else '—'}",
            "",
            "## Owner-only (cannot API)",
            "- Studio rename → **Don't Blink**",
            "- Pin CTA comment on Video #1",
            "",
            "## Calendar",
            "See `data/LAUNCH_CALENDAR.md` — Day 2 security cam (#3) → Day 3 closet (#4) → Day 4 text (#5)",
        ]
    )
    return "\n".join(lines) + "\n"


def write_ops_status(path: Path | None = None) -> Path:
    path = path or (settings.data_dir / "OPS_STATUS.md")
    path.write_text(build_ops_status_markdown(), encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Write data/OPS_STATUS.md")
    parser.add_argument("--stdout", action="store_true", help="Print instead of writing file")
    args = parser.parse_args()
    md = build_ops_status_markdown()
    if args.stdout:
        print(md, end="")
    else:
        path = write_ops_status()
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
