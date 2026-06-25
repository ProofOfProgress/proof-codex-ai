"""Build and cache searchable Codex index."""

from __future__ import annotations

import fnmatch
import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from shorts_bot.codex.chunks import CodexChunk, chunk_markdown, layer_for_path
from shorts_bot.codex.search import CodexSearcher
from shorts_bot.config import settings


def _workspace_root() -> Path:
    return Path.cwd()


def default_codex_globs() -> list[tuple[str, str]]:
    """(glob from repo root, layer override or empty for auto)."""
    return [
        ("course/files/*.md", "course"),
        ("course/verbatim/*.md", "verbatim"),
        ("channel/brand/*.md", "brand"),
        ("data/research/*.md", "research"),
        ("docs/*.md", "docs"),
        ("data/LEARNED.md", "learned"),
        ("data/MEMORY.md", "memory"),
        ("data/operating_rules_seed.md", "ops"),
        ("data/LAUNCH_QUALITY.md", "ops"),
        ("data/LONG_FORM_QUALITY.md", "ops"),
        ("data/PRIORITY_LONG_FORM.md", "ops"),
        ("data/PRIORITIES.md", "ops"),
        ("docs/CODEX.md", "docs"),
        ("docs/CONTENT_FORMATS.md", "docs"),
    ]


def _collect_source_paths(workspace: Path) -> list[Path]:
    paths: list[Path] = []
    seen: set[str] = set()
    for pattern, _layer in default_codex_globs():
        for path in workspace.glob(pattern):
            if not path.is_file():
                continue
            key = str(path.resolve())
            if key in seen:
                continue
            seen.add(key)
            paths.append(path)
    return sorted(paths)


def _fingerprint(paths: list[Path]) -> str:
    parts: list[str] = []
    for p in paths:
        try:
            st = p.stat()
            parts.append(f"{p}:{st.st_mtime_ns}:{st.st_size}")
        except OSError:
            parts.append(f"{p}:missing")
    return hashlib.sha256("|".join(parts).encode()).hexdigest()[:16]


def _chunk_to_dict(c: CodexChunk) -> dict:
    return asdict(c)


def _chunk_from_dict(d: dict) -> CodexChunk:
    return CodexChunk(**d)


class CodexIndex:
    def __init__(self, chunks: list[CodexChunk], *, fingerprint: str = "") -> None:
        self.chunks = chunks
        self.fingerprint = fingerprint
        self._searcher: CodexSearcher | None = None

    @property
    def searcher(self) -> CodexSearcher:
        if self._searcher is None:
            self._searcher = CodexSearcher(self.chunks)
        return self._searcher

    def list_sources(self) -> list[dict[str, str | int]]:
        counts: dict[str, dict[str, str | int]] = {}
        for c in self.chunks:
            row = counts.setdefault(
                c.source_path,
                {"path": c.source_path, "layer": c.layer, "chunks": 0},
            )
            row["chunks"] = int(row["chunks"]) + 1
        return sorted(counts.values(), key=lambda r: str(r["path"]))

    @classmethod
    def build(cls, *, force: bool = False) -> CodexIndex:
        workspace = _workspace_root()
        paths = _collect_source_paths(workspace)
        fp = _fingerprint(paths)
        cache_path = settings.data_dir / "codex_index.json"

        if not force and cache_path.is_file():
            try:
                cached = json.loads(cache_path.read_text(encoding="utf-8"))
                if cached.get("fingerprint") == fp:
                    chunks = [_chunk_from_dict(d) for d in cached.get("chunks", [])]
                    return cls(chunks, fingerprint=fp)
            except (json.JSONDecodeError, TypeError, KeyError):
                pass

        chunks: list[CodexChunk] = []
        for path in paths:
            rel = str(path.relative_to(workspace)).replace("\\", "/")
            layer = layer_for_path(rel)
            for pattern, hint in default_codex_globs():
                if fnmatch.fnmatch(rel, pattern):
                    layer = hint
                    break
            chunks.extend(chunk_markdown(path, layer=layer, workspace=workspace))

        payload = {
            "fingerprint": fp,
            "chunk_count": len(chunks),
            "chunks": [_chunk_to_dict(c) for c in chunks],
        }
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(payload, indent=0), encoding="utf-8")
        return cls(chunks, fingerprint=fp)

    def read_source(self, rel_path: str, *, max_chars: int = 12000) -> str:
        workspace = _workspace_root()
        target = (workspace / rel_path).resolve()
        if not str(target).startswith(str(workspace.resolve())):
            raise ValueError("Path escapes workspace")
        if not target.is_file():
            raise FileNotFoundError(rel_path)
        text = target.read_text(encoding="utf-8")
        if len(text) > max_chars:
            return text[:max_chars] + f"\n\n[… truncated at {max_chars} chars — open file for full text]"
        return text
