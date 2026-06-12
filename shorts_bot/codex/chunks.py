"""Chunk Codex markdown sources for search."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

Layer = str  # course | verbatim | brand | research | docs | learned | memory | ops


@dataclass(frozen=True)
class CodexChunk:
    chunk_id: str
    source_path: str
    layer: Layer
    section: str
    text: str
    line_start: int = 0

    @property
    def citation(self) -> str:
        loc = f":{self.line_start}" if self.line_start else ""
        title = self.section or Path(self.source_path).stem
        return f"{self.source_path}{loc} — {title}"


def _split_long_text(text: str, *, max_chars: int = 1400) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    parts: list[str] = []
    paragraphs = re.split(r"\n\n+", text)
    buf = ""
    for para in paragraphs:
        candidate = f"{buf}\n\n{para}".strip() if buf else para
        if len(candidate) <= max_chars:
            buf = candidate
        else:
            if buf:
                parts.append(buf)
            if len(para) <= max_chars:
                buf = para
            else:
                for i in range(0, len(para), max_chars):
                    parts.append(para[i : i + max_chars])
                buf = ""
    if buf:
        parts.append(buf)
    return parts


def chunk_markdown(
    path: Path,
    *,
    layer: Layer,
    workspace: Path,
    max_chars: int = 1400,
) -> list[CodexChunk]:
    """Split a markdown file by ## headers into searchable chunks."""
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError:
        return []

    rel = str(path.resolve().relative_to(workspace.resolve()))
    chunks: list[CodexChunk] = []
    current_section = Path(path).stem
    current_lines: list[str] = []
    line_start = 1
    section_start = 1

    def flush() -> None:
        nonlocal current_lines, line_start
        body = "\n".join(current_lines).strip()
        if not body or len(body) < 40:
            current_lines = []
            return
        for i, part in enumerate(_split_long_text(body, max_chars=max_chars)):
            cid = f"{rel}#{section_start}:{i}"
            chunks.append(
                CodexChunk(
                    chunk_id=cid,
                    source_path=rel,
                    layer=layer,
                    section=current_section,
                    text=part,
                    line_start=section_start,
                )
            )
        current_lines = []

    for lineno, line in enumerate(raw.splitlines(), start=1):
        if line.startswith("## "):
            flush()
            current_section = line[3:].strip()
            section_start = lineno
            current_lines = []
            continue
        current_lines.append(line)

    flush()
    if not chunks and raw.strip():
        for i, part in enumerate(_split_long_text(raw.strip(), max_chars=max_chars)):
            chunks.append(
                CodexChunk(
                    chunk_id=f"{rel}#0:{i}",
                    source_path=rel,
                    layer=layer,
                    section=current_section,
                    text=part,
                    line_start=1,
                )
            )
    return chunks


def layer_for_path(rel_path: str) -> Layer:
    p = rel_path.replace("\\", "/")
    if p.startswith("course/files/"):
        return "course"
    if p.startswith("course/verbatim/"):
        return "verbatim"
    if p.startswith("channel/brand/"):
        return "brand"
    if p.startswith("data/research/"):
        return "research"
    if p.startswith("docs/"):
        return "docs"
    if p.endswith("LEARNED.md"):
        return "learned"
    if p.endswith("MEMORY.md"):
        return "memory"
    return "ops"
