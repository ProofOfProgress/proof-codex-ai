"""CLI for persistent agent memory (operating rules, preferences, facts)."""

from __future__ import annotations

import argparse
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.memory.agent_memory import get_agent_memory_store


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Soft Continuity agent memory")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="List saved memories")

    add_p = sub.add_parser("add", help="Add a memory")
    add_p.add_argument("content", help="Memory text")
    add_p.add_argument(
        "--category",
        default="fact",
        choices=("operating_rule", "preference", "fact", "context", "decision"),
    )
    add_p.add_argument("--pin", action="store_true", help="Pin memory in exports")

    forget_p = sub.add_parser("forget", help="Delete memory by id")
    forget_p.add_argument("memory_id", type=int)

    export_p = sub.add_parser("export", help="Write MEMORY.md")
    export_p.add_argument("--path", type=Path, default=None)

    import_p = sub.add_parser("import", help="Import markdown sections as memories")
    import_p.add_argument("path", type=Path)
    import_p.add_argument("--category", default="operating_rule")

    args = parser.parse_args(argv)
    store = get_agent_memory_store()

    if args.cmd == "list":
        print(store.format_list())
        return 0
    if args.cmd == "add":
        mem = store.add_memory(
            content=args.content,
            category=args.category,
            source="cli",
            pinned=args.pin,
        )
        print(f"Saved #{mem.id}: {mem.content}")
        return 0
    if args.cmd == "forget":
        ok = store.delete_memory(args.memory_id)
        print("Deleted." if ok else f"No memory #{args.memory_id}")
        return 0 if ok else 1
    if args.cmd == "export":
        path = store.export_markdown(args.path)
        print(path)
        return 0
    if args.cmd == "import":
        count = store.import_markdown(args.path, source="import", category=args.category)
        print(f"Imported {count} section(s) from {args.path}")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
