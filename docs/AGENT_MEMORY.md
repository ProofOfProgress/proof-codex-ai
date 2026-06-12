# Agent memory (ChatGPT-style)

Soft Continuity remembers **operating rules**, **preferences**, and **facts** across sessions so you do not have to re-explain pipeline choices every time.

## Storage

- **SQLite** table `agent_memories` in `data/shorts_bot.db`
- **Markdown export** at `data/MEMORY.md` (updated on every change)
- **Seed file** `data/operating_rules_seed.md` imported on first run

## How memory is used

1. **Strategist chat** — injected into the system prompt; recent chat history is restored on startup
2. **Draft generation** — operating rules included in draft context
3. **Web chat** — same `BotOperations.chat()` router

## Commands

| Where | Command | Action |
|-------|---------|--------|
| Web chat | `remember <text>` | Save a fact or rule |
| Any | `operating rule: <text>` | Save as operating_rule category |
| Any | `memory` / `rules` | List saved memories |
| Any | `forget <id>` | Delete by id |

## CLI

```bash
python3 -m shorts_bot.memory.memory_cli list
python3 -m shorts_bot.memory.memory_cli add "Always CAPTION_MODE=ffmpeg" --category operating_rule --pin
python3 -m shorts_bot.memory.memory_cli export
python3 -m shorts_bot.memory.memory_cli import data/operating_rules_seed.md
```

## Categories

`operating_rule`, `preference`, `fact`, `context`, `decision`

Pinned memories and operating rules appear first in prompts.
