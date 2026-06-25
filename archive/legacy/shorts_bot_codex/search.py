"""BM25 search over Codex chunks — stdlib only, no embedding deps."""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass

from shorts_bot.codex.chunks import CodexChunk

_TOKEN_RE = re.compile(r"[a-z0-9']+")


def tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


@dataclass
class SearchHit:
    chunk: CodexChunk
    score: float


class CodexSearcher:
    """Okapi BM25 over pre-chunked Codex corpus."""

    def __init__(self, chunks: list[CodexChunk], *, k1: float = 1.4, b: float = 0.75) -> None:
        self.chunks = chunks
        self.k1 = k1
        self.b = b
        self._tokens: list[list[str]] = [tokenize(c.text) for c in chunks]
        self._doc_len = [len(t) for t in self._tokens]
        self._avgdl = sum(self._doc_len) / max(1, len(self._doc_len))
        self._df: Counter[str] = Counter()
        for toks in self._tokens:
            for term in set(toks):
                self._df[term] += 1
        self._N = len(chunks)

    def search(self, query: str, *, limit: int = 8) -> list[SearchHit]:
        q_tokens = tokenize(query)
        if not q_tokens or not self.chunks:
            return []

        scores: list[tuple[int, float]] = []
        for idx, doc_tokens in enumerate(self._tokens):
            if not doc_tokens:
                continue
            tf = Counter(doc_tokens)
            dl = self._doc_len[idx]
            score = 0.0
            for term in q_tokens:
                if term not in tf:
                    continue
                df = self._df.get(term, 0)
                idf = math.log(1 + (self._N - df + 0.5) / (df + 0.5))
                freq = tf[term]
                denom = freq + self.k1 * (1 - self.b + self.b * dl / self._avgdl)
                score += idf * (freq * (self.k1 + 1)) / denom
            if score > 0:
                scores.append((idx, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return [
            SearchHit(chunk=self.chunks[i], score=s)
            for i, s in scores[:limit]
        ]
