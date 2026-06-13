"""Check Kling + Replicate setup — run before first paid video generation."""

from __future__ import annotations

import argparse
import sys

from rich.console import Console
from rich.table import Table

console = Console()


def kling_setup_status() -> tuple[bool, list[str]]:
    from shorts_bot.config import settings
    from shorts_bot.production.ai_video_guard import ai_video_generation_enabled
    from shorts_bot.production.images.replicate import probe_replicate

    lines: list[str] = []
    ok = True

    def check(name: str, passed: bool, detail: str) -> None:
        nonlocal ok
        if not passed:
            ok = False
        lines.append(f"{'OK' if passed else 'FIX'} {name}: {detail}")

    check(
        "Replicate token",
        settings.has_replicate_images,
        "set REPLICATE_API_TOKEN in Cursor Secrets (starts with r8_)",
    )
    check(
        "Video backend",
        settings.uses_kling_video,
        f"VIDEO_BACKEND={settings.video_backend!r} (want kling)",
    )
    check(
        "Generation enabled",
        ai_video_generation_enabled(),
        "set AI_VIDEO_GENERATION_ENABLED=true in Cursor Secrets",
    )
    check(
        "Visual style",
        settings.visual_style in ("ai_video", "ai", "hybrid"),
        f"VISUAL_STYLE={settings.visual_style!r} (ai_video recommended)",
    )
    check(
        "Native audio",
        settings.kling_generate_audio and settings.kling_skip_narrator_tts,
        "KLING_GENERATE_AUDIO=true + KLING_SKIP_NARRATOR_TTS=true",
    )

    if settings.has_replicate_images:
        reachable, msg = probe_replicate(
            settings.replicate_api_token or "",
            settings.kling_model,
        )
        check("Kling model on Replicate", reachable, msg)
    else:
        check("Kling model on Replicate", False, "needs REPLICATE_API_TOKEN first")

    lines.append(
        f"Plan: {settings.kling_clips_per_short} clips × {settings.kling_clip_seconds}s "
        f"({settings.kling_model}, {settings.kling_mode})"
    )
    return ok, lines


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify Kling 3.0 + Replicate is ready for PERIPHERAL Shorts"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Machine-readable output",
    )
    args = parser.parse_args()

    ready, lines = kling_setup_status()

    if args.json:
        import json

        print(json.dumps({"ready": ready, "checks": lines}, indent=2))
        raise SystemExit(0 if ready else 1)

    table = Table(title="Kling setup")
    table.add_column("Status", style="bold")
    table.add_column("Detail")
    for line in lines:
        if line.startswith("OK "):
            table.add_row("[green]OK[/green]", line[3:])
        elif line.startswith("FIX "):
            table.add_row("[red]FIX[/red]", line[4:])
        else:
            table.add_row("", line)
    console.print(table)

    if ready:
        console.print(
            "\n[green]Ready.[/green] Test (costs ~2 Replicate runs):\n"
            "  python3 -m shorts_bot.production.daily_cli --topic \"village eye dream\" --no-upload"
        )
    else:
        console.print(
            "\n[yellow]Not ready yet.[/yellow] Add the FIX items in "
            "[bold]Cursor → Cloud Agent → Secrets[/bold], then run:\n"
            "  bash scripts/install.sh\n"
            "  python3 -m shorts_bot.production.kling_setup_cli"
        )
    raise SystemExit(0 if ready else 1)


if __name__ == "__main__":
    main()
