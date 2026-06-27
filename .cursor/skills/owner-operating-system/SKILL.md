---
name: owner-operating-system
description: How owner tips, agent memory, and skills work together. Use when owner adds rules, wants learning across sessions, or asks how the bot remembers things.
---

# Owner operating system (learning without burning compute)

## Three layers

| Layer | File / tool | Cost | Purpose |
|-------|-------------|------|---------|
| **Tips registry** | `data/operating_tips.json` | Free | Owner's numbered rules (grow to 100+). Some enforced by Python, some agent-only. |
| **Agent memory** | `python3 -m shorts_bot.memory.memory_cli` + `data/MEMORY.md` | Free | Pinned rules exported for every session bootstrap. |
| **Pre-publish gate** | `scripts/pre_publish_gate.py` | Cheap / optional vision | Blocks upload in **code** — not in Cursor chat. |

Read `AGENTS.md` + skim `data/MEMORY.md` at session start. Do **not** re-read entire course unless creative work requires it.

## Owner adds a tip

1. Edit `data/operating_tips.json` **or** run:

```bash
python3 -m shorts_bot.operating.tips_cli add --id T011 --title "..." --content "..." \
  --applies-to agent --enforcement agent
```

2. For agent-visible tips, sync to memory:

```bash
python3 -m shorts_bot.operating.tips_cli sync-memory
```

3. For **code-enforced** tips, set `enforcement: both` and a `code_check` — extend `pre_publish_gate.py` if new check type needed.

## Enforcement types

- `code` — Python gate only (no agent discretion)
- `agent` — skill + memory (follow in chat)
- `both` — gate + agent

## What I can add without owner OAuth

- Skills in `.cursor/skills/`
- Tips JSON + memory sync
- Python QC gates
- Docs and AGENTS.md pointers

## What needs owner in Cursor UI

- MCP plugins (OAuth): Higgsfield, Slack, Notion, etc.
- Dashboard → Integrations → enable for Cloud Agents → **new agent run**

## Creativity default

Execute course + owner tips + explicit orders. Do not invent hooks or strategy unless owner asks.
