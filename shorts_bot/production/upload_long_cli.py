"""Upload long-form compilation with QC gate + chapter metadata."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rich.console import Console

from shorts_bot.config import settings
from shorts_bot.production.long_quality import assess_long_quality
from shorts_bot.production.long_upload_meta import package_from_pack_dir, write_long_upload_files
from shorts_bot.youtube.upload import upload_video

console = Console()


def upload_long_compilation(
    pack_dir: Path,
    *,
    video_path: Path | None = None,
    visibility: str = "public",
    strict_qc: bool = False,
) -> str:
    report = assess_long_quality(pack_dir, strict_duration=strict_qc)
    if not report.passed:
        raise RuntimeError(
            "Long QC failed:\n" + "\n".join(report.summary_lines())
        )

    manifest_path = pack_dir / "manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(manifest_path)

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    output_name = str(manifest.get("output_video") or "final_long.mp4")
    video = video_path or (pack_dir / output_name)
    if not video.is_file():
        raise FileNotFoundError(video)

    package = package_from_pack_dir(pack_dir)
    package.visibility = visibility
    write_long_upload_files(pack_dir, package, pack_id=pack_dir.name)

    up = upload_video(
        video,
        title=package.title,
        description=package.description,
        tags=package.tags,
        visibility=visibility,
    )
    return up.video_url


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload Peripheral long compilation (QC gated)")
    parser.add_argument("--pack-dir", type=Path, required=True)
    parser.add_argument("--video", type=Path, default=None)
    parser.add_argument("--visibility", choices=("public", "unlisted", "private"), default="public")
    parser.add_argument("--strict-qc", action="store_true")
    args = parser.parse_args()

    url = upload_long_compilation(
        args.pack_dir,
        video_path=args.video,
        visibility=args.visibility,
        strict_qc=args.strict_qc,
    )
    console.print(f"[green]Uploaded: {url}[/green]")


if __name__ == "__main__":
    main()
