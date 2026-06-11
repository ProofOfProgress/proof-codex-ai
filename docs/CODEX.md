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

- `shorts_bot/codex/` — name + `load_codex()` helper
- `shorts_bot/course/loader.py` — `CourseKnowledgeBase` loads Codex files 01–09
- `shorts_bot/course/router.py` — routes messages to the right Codex files

## Owner-facing language

Say **Codex**, not "course KB", "knowledge base upload", or "Jenny files" — unless you're pointing at a specific file path.
