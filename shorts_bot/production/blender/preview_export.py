"""Export PNG previews + WATCH.md so owner never needs Blender or Cursor video player."""

from __future__ import annotations

import subprocess
from pathlib import Path


def export_preview_assets(pack_dir: Path, *, draft_id: int) -> Path:
    """Extract stills from final_short + clips; write owner watch guide."""
    pack_dir = Path(pack_dir)
    frames_dir = pack_dir / "preview_frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    final = pack_dir / "final_short.mp4"
    clips = sorted((pack_dir / "clips").glob("blender_part_*.mp4")) if (pack_dir / "clips").is_dir() else []

    targets: list[tuple[str, Path, float]] = []
    if final.is_file():
        for sec, name in ((0.0, "full_0s"), (5.0, "full_5s"), (15.0, "full_15s"), (25.0, "full_25s")):
            targets.append((name, final, sec))
    for clip in clips[:3]:
        stem = clip.stem.replace("blender_part_", "clip_")
        targets.append((f"{stem}_mid", clip, 5.0))

    for name, video, sec in targets:
        out = frames_dir / f"{name}.png"
        subprocess.run(
            [
                "ffmpeg", "-y", "-ss", str(sec), "-i", str(video),
                "-frames:v", "1", "-q:v", "2", str(out),
            ],
            capture_output=True,
            check=False,
        )

    # Contact sheet from final if available
    if final.is_file():
        sheet = frames_dir / "full_contact_sheet.png"
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", str(final),
                "-vf", "fps=1/5,scale=360:-1,tile=3x2",
                "-frames:v", "1", str(sheet),
            ],
            capture_output=True,
            check=False,
        )

    watch = pack_dir / "WATCH.md"
    lines = [
        f"# How to watch draft #{draft_id} (no Blender on your PC needed)",
        "",
        "All rendering happens in the **cloud**. Your computer only opens links or pictures.",
        "",
        "## Option 1 — Browser (video player)",
        "",
        "1. Ask the agent to start the web UI, or run on the cloud machine: `python3 -m shorts_bot.web`",
        f"2. Open **http://127.0.0.1:8080/preview/draft/{draft_id}** (use Cursor port-forward if remote)",
        "",
        "## Option 2 — Pictures in Cursor (always works)",
        "",
        "Open these PNG files in the file tree:",
        "",
        f"- `{frames_dir.relative_to(pack_dir)}/full_contact_sheet.png` — 6 frames from the full Short",
        f"- `{frames_dir.relative_to(pack_dir)}/full_15s.png` — middle of the video (wave beat)",
        "",
        "## Option 3 — Google Drive",
        "",
        "Upload `final_short.mp4` to Drive → share link → watch on phone.",
        "",
        "## Option 4 — YouTube unlisted",
        "",
        "Only for owner-approved final versions (not every test render).",
        "",
        "## Files",
        "",
    ]
    if final.is_file():
        lines.append(f"- Full Short: `{final.name}` ({final.stat().st_size // 1024} KB)")
    for clip in clips:
        lines.append(f"- Clip: `clips/{clip.name}`")
    lines.append("")
    lines.append("*Auto-generated after Blender produce — do not hand-edit.*")
    watch.write_text("\n".join(lines), encoding="utf-8")
    return watch
