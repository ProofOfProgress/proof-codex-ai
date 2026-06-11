"""Upload every saved render for a draft as unlisted, oldest-first (improvement timeline)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rich.console import Console

from shorts_bot.config import settings
from shorts_bot.production.upload_unlisted_cli import upload_existing_video

console = Console()

# Known draft #3 iteration files in creation order (oldest → newest).
DRAFT_3_BUILD_SERIES: list[tuple[str, str]] = [
    ("final_short_sync_test.mp4", "(build v1 sync)"),
    ("final_short_fixed.mp4", "(build v2 fixed)"),
    ("final_short_jumpscare_clip.mp4", "(build v3 jumpscare)"),
    ("final_short_ui.mp4", "(build v4 UI)"),
    ("final_short_voice_caps.mp4", "(build v5 captions)"),
    ("final_short_unlisted.mp4", "(build v6 scrub+regen)"),
    ("final_short.mp4", "(build v7 latest)"),
]


def upload_build_series(
    draft_id: int,
    *,
    pack_dir: Path | None = None,
    series: list[tuple[str, str]] | None = None,
    skip_existing_titles: bool = True,
) -> list[str]:
    """Upload each file in order; returns YouTube URLs."""
    root = pack_dir or (settings.data_dir / "production" / f"draft_{draft_id}")
    entries = series or DRAFT_3_BUILD_SERIES
    log_path = root / "upload_series_log.json"
    prior: dict[str, str] = {}
    if log_path.exists():
        try:
            prior = json.loads(log_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            prior = {}

    urls: list[str] = []
    uploaded: dict[str, str] = dict(prior)

    for filename, suffix in entries:
        video = root / filename
        if not video.exists():
            console.print(f"[yellow]Skip missing {filename}[/yellow]")
            continue
        key = f"{filename}|{suffix}"
        if skip_existing_titles and key in uploaded:
            url = uploaded[key]
            console.print(f"[dim]Already uploaded {filename} → {url}[/dim]")
            urls.append(url)
            continue
        console.print(f"[cyan]Uploading {filename} {suffix}…[/cyan]")
        try:
            msg = upload_existing_video(
                draft_id,
                video,
                pack_dir=root,
                title_suffix=suffix,
                allow_duplicate_draft=True,
            )
            url = msg.split("OK: ")[-1].strip()
            uploaded[key] = url
            urls.append(url)
            console.print(f"[green]{msg}[/green]")
        except Exception as exc:
            console.print(f"[red]{filename} failed: {exc}[/red]")

    log_path.write_text(json.dumps(uploaded, indent=2), encoding="utf-8")
    return urls


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload all draft builds unlisted, oldest first")
    parser.add_argument("--draft-id", type=int, default=3)
    parser.add_argument("--pack-dir", type=Path, default=None)
    parser.add_argument("--force", action="store_true", help="Re-upload even if logged")
    args = parser.parse_args()
    urls = upload_build_series(
        args.draft_id,
        pack_dir=args.pack_dir,
        skip_existing_titles=not args.force,
    )
    console.print("\n[bold]Upload timeline (oldest → newest):[/bold]")
    for i, url in enumerate(urls, 1):
        console.print(f"  {i}. {url}")


if __name__ == "__main__":
    main()
