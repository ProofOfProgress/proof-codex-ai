"""CLI — import owner tips into agent memory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from shorts_bot.operating.tips import load_tips, tips_path, format_all_agent_tips
from shorts_bot.memory.agent_memory import get_agent_memory_store


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Operating tips registry")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="List tips from data/operating_tips.json")
    sub.add_parser("checklist", help="Print agent checklist (no LLM)")

    add_p = sub.add_parser("add", help="Append a tip to operating_tips.json")
    add_p.add_argument("--id", required=True, help="Tip id e.g. T011")
    add_p.add_argument("--title", required=True)
    add_p.add_argument("--content", required=True)
    add_p.add_argument(
        "--applies-to",
        nargs="+",
        default=["agent"],
        help="video carousel affiliate agent",
    )
    add_p.add_argument("--enforcement", default="agent", choices=("code", "agent", "both"))
    add_p.add_argument("--code-check", default="", help="aigc_configured, caption_bans, etc.")

    sync_p = sub.add_parser("sync-memory", help="Import agent/both tips into SQLite memory + MEMORY.md")
    sync_p.add_argument("--replace", action="store_true", help="Skip tips already titled with same id")

    args = parser.parse_args(argv)
    path = tips_path()

    if args.cmd == "list":
        for t in load_tips(path):
            print(f"{t.id} [{t.enforcement}] {t.title} — {t.content[:80]}")
        return 0

    if args.cmd == "checklist":
        print(format_all_agent_tips())
        return 0

    if args.cmd == "add":
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
        else:
            data = {"tips": []}
        tips = data.get("tips") or []
        tips.append(
            {
                "id": args.id,
                "title": args.title,
                "content": args.content,
                "applies_to": args.applies_to,
                "enforcement": args.enforcement,
                "code_check": args.code_check or None,
            }
        )
        data["tips"] = tips
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        print(f"Added {args.id} → {path}")
        return 0

    if args.cmd == "sync-memory":
        store = get_agent_memory_store()
        existing = {m.title for m in store.list_memories(limit=500)}
        count = 0
        for tip in load_tips(path):
            if tip.enforcement not in ("agent", "both"):
                continue
            title = f"Tip {tip.id} — {tip.title}"
            if args.replace and title in existing:
                continue
            if title in existing:
                continue
            store.add_memory(
                category="operating_rule",
                title=title,
                content=tip.content,
                source="operating_tips",
                pinned=False,
            )
            count += 1
        store.export_markdown()
        print(f"Synced {count} tip(s) to agent memory")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
