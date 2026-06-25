# Codex

**Codex** is the Shorts Bot knowledge base — the single name for everything agents read before they strategize, draft, or QC.

## What lives in Codex

| Layer | Location | Purpose |
|-------|----------|---------|
| **Strategist core** | `course/files/01–09_*.md` | Jenny Hoyos retention, hooks, visuals, payoff |
| **Verbatim rules** | `course/verbatim/` | Non-negotiable transcript constraints |
| **Router** | `course/router_prompt.md` | How to pick files 01–09 per question |
| **Brand & world** | `channel/brand/` | Peripheral identity, **The Gap**, analog horror lane |
| **Research** | `data/research/` | Horror psychology, SEO, applied learnings |
| **Learned rules** | `data/LEARNED.md` | Auto-approved improvements from reward sync |
| **Agent memory** | `data/MEMORY.md` + SQLite | Owner operating rules, preferences, facts |

## Code

- `shorts_bot/codex/` — BM25 index + search (agent-internal)
- `shorts_bot/course/loader.py` — `CourseKnowledgeBase` loads Codex files 01–09
- `shorts_bot/course/router.py` — routes messages to the right Codex files

## Who uses Codex search

| Who | How |
|-----|-----|
| **AlphaBeta001** (Chief Manager) | Auto — BM25 passages injected before every strategy reply (`codex/context.py`) |
| **Cloud agents** (Cursor) | `python3 -m shorts_bot.codex search "…"` in terminal when working |
| **Owner** | Does **not** use Codex directly — ask AlphaBeta001 or chat normally |

There is no owner-facing `!codex`, web button, or chat command. That keeps context load off the human and on the agent.

## Owner-facing language

Say **Codex**, not "course KB", "knowledge base upload", or "Jenny files" — unless you're pointing at a specific file path.
