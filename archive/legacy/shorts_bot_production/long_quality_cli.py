"""CLI: long-form quality gate."""

from __future__ import annotations

import argparse
import sys

from rich.console import Console

from shorts_bot.production.long_quality import assess_long_quality

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(description="Long-form QC before upload")
    parser.add_argument("--pack-dir", type=str, required=True)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail if duration below 8 min target (bridge VO not added yet)",
    )
    args = parser.parse_args()

    from pathlib import Path

    report = assess_long_quality(Path(args.pack_dir), strict_duration=args.strict)
    for line in report.summary_lines():
        if line.startswith("Long QC") and "FAIL" in line:
            console.print(f"[red]{line}[/red]")
        elif "[issue]" in line:
            console.print(f"[red]{line}[/red]")
        elif "[warn]" in line:
            console.print(f"[yellow]{line}[/yellow]")
        else:
            console.print(line)

    if not report.passed:
        sys.exit(1)


if __name__ == "__main__":
    main()
