"""Generate MP3 voiceover for a production pack."""

from __future__ import annotations

import argparse

from rich.console import Console

from shorts_bot.config import settings
from shorts_bot.memory.store import MemoryStore
from shorts_bot.production.voiceover import DEFAULT_VOICE, generate_voiceover, list_voices

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate voiceover MP3 for a draft production pack.")
    parser.add_argument("--draft-id", type=int, required=True)
    parser.add_argument("--voice", default=DEFAULT_VOICE, choices=list_voices())
    args = parser.parse_args()

    store = MemoryStore(settings.database_path)
    draft = store.get_draft(args.draft_id)
    pack_dir = settings.data_dir / "production" / f"draft_{args.draft_id}"
    script_path = pack_dir / "VOICEOVER_SCRIPT.txt"
    script = script_path.read_text(encoding="utf-8") if script_path.exists() else draft.script

    result = generate_voiceover(
        pack_dir,
        draft_id=args.draft_id,
        script_text=script,
        voice=args.voice,
    )
    console.print(f"[green]{result.message}[/green]")
    console.print(f"[cyan]Duration hint:[/cyan] {result.duration_hint}")


if __name__ == "__main__":
    main()
