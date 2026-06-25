"""Codex CLI — ask, search, read, list."""

from __future__ import annotations

import argparse
import json
import sys

from rich.console import Console
from rich.table import Table

from shorts_bot.codex.ask import ask_codex, search_codex
from shorts_bot.codex.index import CodexIndex

console = Console()


def cmd_ask(args: argparse.Namespace) -> int:
    result = ask_codex(args.question, search_only=args.search_only)
    console.print(result.answer)
    if args.json:
        console.print_json(
            data={
                "question": result.question,
                "mode": result.mode,
                "router_lever": result.router_lever,
                "router_files": result.router_files,
                "sources": result.sources,
                "message": result.message,
            }
        )
    elif result.sources and args.verbose:
        console.print("\n[dim]Sources:[/dim]")
        for s in result.sources:
            console.print(f"  [{s['score']}] {s['citation']}")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    hits = search_codex(args.query, limit=args.limit)
    if args.json:
        console.print_json(
            data=[
                {
                    "score": h.score,
                    "path": h.chunk.source_path,
                    "section": h.chunk.section,
                    "layer": h.chunk.layer,
                    "preview": h.chunk.text[:400],
                }
                for h in hits
            ]
        )
        return 0

    table = Table(title=f"Codex search: {args.query}")
    table.add_column("Score", justify="right")
    table.add_column("Layer")
    table.add_column("Source")
    table.add_column("Preview")

    for h in hits:
        preview = h.chunk.text[:120].replace("\n", " ")
        table.add_row(
            f"{h.score:.2f}",
            h.chunk.layer,
            h.chunk.citation[:60],
            preview + "…",
        )
    console.print(table)
    return 0 if hits else 1


def cmd_read(args: argparse.Namespace) -> int:
    idx = CodexIndex.build()
    try:
        text = idx.read_source(args.path, max_chars=args.max_chars)
    except (FileNotFoundError, ValueError) as exc:
        console.print(f"[red]{exc}[/red]")
        return 1
    console.print(text)
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    idx = CodexIndex.build(force=args.rebuild)
    sources = idx.list_sources()
    if args.json:
        console.print_json(
            data={
                "chunk_count": len(idx.chunks),
                "fingerprint": idx.fingerprint,
                "sources": sources,
            }
        )
        return 0

    table = Table(title=f"Codex index ({len(idx.chunks)} chunks)")
    table.add_column("Layer")
    table.add_column("Path")
    table.add_column("Chunks", justify="right")
    for row in sources:
        table.add_row(str(row["layer"]), str(row["path"]), str(row["chunks"]))
    console.print(table)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Codex — search knowledge base + optional Gemini answer",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    ask_p = sub.add_parser("ask", help="Search Codex and answer with Gemini")
    ask_p.add_argument("question", help="e.g. 'how do I build suspense in a horror short?'")
    ask_p.add_argument(
        "--search-only",
        action="store_true",
        help="Return ranked passages only (no LLM)",
    )
    ask_p.add_argument("--json", action="store_true", help="Also print source metadata as JSON")
    ask_p.add_argument("-v", "--verbose", action="store_true", help="List sources after answer")
    ask_p.set_defaults(func=cmd_ask)

    search_p = sub.add_parser("search", help="BM25 search — manual browse")
    search_p.add_argument("query")
    search_p.add_argument("--limit", type=int, default=8)
    search_p.add_argument("--json", action="store_true")
    search_p.set_defaults(func=cmd_search)

    read_p = sub.add_parser("read", help="Read a Codex file by path")
    read_p.add_argument("path", help="e.g. data/research/HORROR_PSYCHOLOGY_DEEP_RESEARCH.md")
    read_p.add_argument("--max-chars", type=int, default=12000)
    read_p.set_defaults(func=cmd_read)

    list_p = sub.add_parser("list", help="List indexed sources")
    list_p.add_argument("--rebuild", action="store_true", help="Force rebuild index cache")
    list_p.add_argument("--json", action="store_true")
    list_p.set_defaults(func=cmd_list)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
