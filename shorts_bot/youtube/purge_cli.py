"""Purge channel videos + local production drafts (fresh niche start)."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from rich.console import Console
from rich.table import Table

from shorts_bot.config import settings
from shorts_bot.memory.store import MemoryStore
from shorts_bot.youtube.channel_videos import list_channel_videos
from shorts_bot.youtube.delete import delete_all_channel_videos

console = Console()


def _purge_local_production() -> list[str]:
    removed: list[str] = []
    prod = settings.data_dir / "production"
    if prod.exists():
        for child in prod.iterdir():
            if child.is_dir() and child.name.startswith("draft_"):
                shutil.rmtree(child)
                removed.append(str(child))
    research = settings.data_dir / "research"
    if research.exists():
        shutil.rmtree(research)
        removed.append(str(research))
    return removed


def _reset_channel_state(store: MemoryStore) -> None:
    store.set_channel_state("daily_topic_index", "0")
    store.set_channel_state("niche_version", "v2_minute_before")
    store.set_channel_state("last_topic_pick", "")


def main() -> None:
    parser = argparse.ArgumentParser(description="Delete all YT videos + local draft packs.")
    parser.add_argument("--dry-run", action="store_true", help="List only, do not delete")
    parser.add_argument("--local-only", action="store_true", help="Skip YouTube API delete")
    parser.add_argument("--youtube-only", action="store_true", help="Skip local file purge")
    args = parser.parse_args()

    if not args.local_only:
        try:
            videos = list_channel_videos()
            if videos:
                table = Table(title="Channel videos")
                table.add_column("ID")
                table.add_column("Title")
                for v in videos[:30]:
                    table.add_row(v.video_id, v.title[:60])
                console.print(table)
            else:
                console.print("[yellow]No videos on channel.[/yellow]")

            result = delete_all_channel_videos(dry_run=args.dry_run)
            console.print(f"[green]{result.message}[/green]")
            for vid, err in result.failed:
                console.print(f"[red]Failed {vid}: {err}[/red]")
        except Exception as exc:
            console.print(f"[red]YouTube purge failed: {exc}[/red]")

    if not args.youtube_only:
        if args.dry_run:
            dirs = list((settings.data_dir / "production").glob("draft_*"))
            console.print(f"Dry run: would remove {len(dirs)} local draft folder(s).")
        else:
            removed = _purge_local_production()
            store = MemoryStore(settings.database_path)
            with store._connect() as conn:
                conn.execute("DELETE FROM drafts")
                conn.execute("DELETE FROM feedback")
            _reset_channel_state(store)
            console.print(f"[green]Purged {len(removed)} local pack(s); cleared draft DB.[/green]")


if __name__ == "__main__":
    main()
