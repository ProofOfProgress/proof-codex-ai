"""Web browsing research — search + page snippets + YouTube autocomplete."""

from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass, field

from shorts_bot.config import settings

_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


@dataclass
class WebSnippet:
    title: str
    url: str
    snippet: str
    source: str


@dataclass
class WebGatherResult:
    topic: str
    queries: list[str] = field(default_factory=list)
    snippets: list[WebSnippet] = field(default_factory=list)
    youtube_suggestions: list[str] = field(default_factory=list)

    def context_block(self, *, max_chars: int = 3500) -> str:
        if not self.snippets and not self.youtube_suggestions:
            return ""
        lines = ["WEB RESEARCH (live — cite gaps, do not invent stats):"]
        if self.youtube_suggestions:
            lines.append("YouTube search suggestions:")
            for s in self.youtube_suggestions[:12]:
                lines.append(f"- {s}")
        for sn in self.snippets:
            line = f"- [{sn.source}] {sn.title}: {sn.snippet[:280]}"
            if sn.url:
                line += f" ({sn.url})"
            lines.append(line)
        text = "\n".join(lines)
        return text[:max_chars]


def _http_get(url: str, *, timeout: int = 15) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _strip_html(html: str) -> str:
    text = re.sub(r"(?is)<script.*?>.*?</script>", " ", html)
    text = re.sub(r"(?is)<style.*?>.*?</style>", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _search_queries(topic: str) -> list[str]:
    base = topic.strip()
    return [
        base,
        f"{base} youtube shorts",
        f"the minute before {base}",
        f"{base} anxiety calm tips",
    ]


def _duckduckgo_snippets(query: str, *, limit: int = 4) -> list[WebSnippet]:
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    try:
        html = _http_get(url, timeout=12)
    except OSError:
        return []
    out: list[WebSnippet] = []
    for m in re.finditer(
        r'class="result__a"[^>]*href="([^"]+)"[^>]*>([^<]+)</a>.*?class="result__snippet"[^>]*>([^<]+)',
        html,
        flags=re.S,
    ):
        href, title, snippet = m.group(1), _strip_html(m.group(2)), _strip_html(m.group(3))
        if "duckduckgo.com/y.js" in href:
            continue
        out.append(WebSnippet(title=title[:120], url=href, snippet=snippet[:400], source="web_search"))
        if len(out) >= limit:
            break
    return out


def _tavily_snippets(query: str, *, limit: int = 4) -> list[WebSnippet]:
    key = (settings.tavily_api_key or "").strip()
    if not key:
        return []
    payload = json.dumps(
        {
            "api_key": key,
            "query": query,
            "search_depth": "basic",
            "max_results": limit,
            "include_answer": True,
        }
    ).encode()
    req = urllib.request.Request(
        "https://api.tavily.com/search",
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": _USER_AGENT},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode())
    except OSError:
        return []
    out: list[WebSnippet] = []
    answer = str(data.get("answer") or "").strip()
    if answer:
        out.append(WebSnippet(title="Tavily summary", url="", snippet=answer[:500], source="tavily"))
    for row in data.get("results") or []:
        out.append(
            WebSnippet(
                title=str(row.get("title", ""))[:120],
                url=str(row.get("url", "")),
                snippet=str(row.get("content", ""))[:400],
                source="tavily",
            )
        )
    return out[:limit]


def _youtube_autocomplete(topic: str, *, limit: int = 12) -> list[str]:
    q = urllib.parse.quote(topic)
    url = f"http://suggestqueries.google.com/complete/search?client=firefox&ds=yt&q={q}"
    try:
        raw = _http_get(url, timeout=8)
    except OSError:
        return []
    # JSONP: window.google.ac.h(["query", [["suggestion",0],...],...])
    m = re.search(r"\[(\[.*\])\s*,\s*\{", raw, flags=re.S)
    if not m:
        return []
    try:
        suggestions = json.loads(m.group(1))
    except json.JSONDecodeError:
        return []
    out: list[str] = []
    for item in suggestions:
        if isinstance(item, list) and item:
            text = str(item[0]).strip()
            if text and text.lower() != topic.lower():
                out.append(text)
        if len(out) >= limit:
            break
    return out


def _fetch_page_snippet(url: str, *, max_chars: int = 500) -> str:
    if not url or not url.startswith("http"):
        return ""
    try:
        html = _http_get(url, timeout=10)
    except OSError:
        return ""
    text = _strip_html(html)
    return text[:max_chars]


def gather_web_context(topic: str, *, max_snippets: int | None = None) -> WebGatherResult:
    """Search the web + YouTube suggestions for deep research context."""
    limit = max_snippets or settings.research_max_web_snippets
    queries = _search_queries(topic)
    snippets: list[WebSnippet] = []
    seen_urls: set[str] = set()

    primary = queries[0]
    for sn in _tavily_snippets(primary, limit=min(5, limit)):
        if sn.url and sn.url in seen_urls:
            continue
        if sn.url:
            seen_urls.add(sn.url)
        snippets.append(sn)

    if len(snippets) < limit:
        for q in queries[:2]:
            for sn in _duckduckgo_snippets(q, limit=3):
                if sn.url and sn.url in seen_urls:
                    continue
                if sn.url:
                    seen_urls.add(sn.url)
                snippets.append(sn)
                if len(snippets) >= limit:
                    break
            if len(snippets) >= limit:
                break

    # Enrich top 2 URLs with page text
    enriched = 0
    for i, sn in enumerate(snippets):
        if enriched >= 2 or not sn.url:
            continue
        extra = _fetch_page_snippet(sn.url)
        if extra and len(extra) > len(sn.snippet):
            snippets[i] = WebSnippet(
                title=sn.title,
                url=sn.url,
                snippet=extra[:600],
                source=sn.source + "+page",
            )
            enriched += 1

    yt = _youtube_autocomplete(topic)
    for q in queries[1:3]:
        for s in _youtube_autocomplete(q):
            if s not in yt:
                yt.append(s)

    return WebGatherResult(
        topic=topic,
        queries=queries,
        snippets=snippets[:limit],
        youtube_suggestions=yt[:15],
    )
