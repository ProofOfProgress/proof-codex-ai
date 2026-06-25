"""List duplicate channel uploads — manual cleanup in YouTube Studio."""

from __future__ import annotations

import argparse
import re
from collections import defaultdict

from rich.console import Console
from rich.table import Table

console = Console()


def _norm(title: str) -> str:
    t = re.sub(r"\s+", " ", title.strip().lower())
    t = re.sub(r"\s*\(v\d+[^)]*\)\s*$", "", t)
    return t


def main() -> None:
    parser = argparse.ArgumentParser(description="Find duplicate uploads on your channel.")
    parser.add_argument("--topic", default="office bathroom", help="Filter titles containing this phrase")
    args = parser.parse_args()

    from shorts_bot.youtube.channel_videos import list_channel_videos

    videos = list_channel_videos(max_results=100)
    needle = args.topic.lower()
    filtered = [v for v in videos if needle in v.title.lower() or needle in _norm(v.title)]

    by_title: dict[str, list] = defaultdict(list)
    for v in filtered:
        by_title[_norm(v.title)].append(v)

    table = Table(title=f"Uploads matching “{args.topic}”")
    table.add_column("Video ID")
    table.add_column("Published")
    table.add_column("Title")

    dupes = 0
    for _key, group in sorted(by_title.items(), key=lambda x: -len(x[1])):
        for i, v in enumerate(sorted(group, key=lambda x: x.published_at, reverse=True)):
            mark = "KEEP (newest)" if i == 0 and len(group) > 1 else ("DUPLICATE" if len(group) > 1 else "")
            if mark == "DUPLICATE":
                dupes += 1
            table.add_row(v.video_id, (v.published_at or "")[:10], v.title[:70] + (f" [{mark}]" if mark else ""))

    console.print(table)
    if dupes:
        console.print(
            f"\n[yellow]{dupes} duplicate(s) — delete extras in Studio → Content. "
            "Keep the best version (usually v2 aligned).[/yellow]"
        )
    else:
        console.print("\n[green]No duplicate title groups found for that filter.[/green]")


if __name__ == "__main__":
    main()
