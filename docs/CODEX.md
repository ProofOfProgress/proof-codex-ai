# Codex

**Codex** is the Shorts Bot knowledge base — the single name for everything agents read before they strategize, draft, or QC.

## What lives in Codex

| Layer | Location | Purpose |
|-------|----------|---------|
| **Strategist core** | `course/files/01–09_*.md` | Jenny Hoyos retention, hooks, visuals, payoff |
| **Verbatim rules** | `course/verbatim/` | Non-negotiable transcript constraints |
| **Router** | `course/router_prompt.md` | How to pick files 01–09 per question |
| **Brand & world** | `channel/brand/` | Don't Blink identity, **The Gap**, analog horror lane |
| **Research** | `data/research/` | Horror psychology, SEO, applied learnings |
| **Learned rules** | `data/LEARNED.md` | Auto-approved improvements from reward sync |
| **Agent memory** | `data/MEMORY.md` + SQLite | Owner operating rules, preferences, facts |

## Code

- `shorts_bot/codex/` — search index, ask (Gemini + citations), CLI
- `shorts_bot/course/loader.py` — `CourseKnowledgeBase` loads Codex files 01–09
- `shorts_bot/course/router.py` — routes messages to the right Codex files (lever 01–09)

## Ask Codex (search + optional Gemini)

Two ways to use the same knowledge — pick what fits:

| Mode | When | Command |
|------|------|---------|
| **Ask** | Plain-English question, want an answer with sources | `python3 -m shorts_bot.codex ask "how do I build suspense in my horror short?"` |
| **Search** | You want ranked passages to read yourself | `python3 -m shorts_bot.codex search suspense retention` |
| **Read** | Open one file in full | `python3 -m shorts_bot.codex read data/research/HORROR_PSYCHOLOGY_DEEP_RESEARCH.md` |
| **List** | See what is indexed | `python3 -m shorts_bot.codex list` |

- **Search base:** BM25 over chunked markdown (course, brand, research, docs, LEARNED/MEMORY when present). Cache: `data/codex_index.json`.
- **LLM:** Gemini (or OpenAI) synthesizes an answer **only from retrieved passages** + router context. Without an API key, `ask` falls back to search-only.
- **Chat tools:** `ask_codex`, `search_codex`, `read_codex_file` (same as CLI from Discord/web agent).
- **Manual routing still works:** `course <question>` or `get_course_guidance` for Jenny files 01–09 only.

## Owner-facing language

Say **Codex**, not "course KB", "knowledge base upload", or "Jenny files" — unless you're pointing at a specific file path.
