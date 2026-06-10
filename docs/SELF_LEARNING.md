# Self-learning model

Soft Continuity learns from **your decisions** and **YouTube performance** — then injects rules into the next draft and strategist chat.

## Loop

```
YouTube sync / manual score → RewardEngine → improvement proposal (max 3/sync)
Draft Yes/No → immediate avoid/repeat rules (no second approval)
Improvement Yes/No → applied training rules
All rules → DraftGenerator + ShortsBotAgent system prompt
```

## What you approve

| Input | What happens immediately | What needs Yes/No |
|-------|--------------------------|-------------------|
| **Reject draft** | `avoid:*` rule in training_config | Nothing extra |
| **Approve draft** | `repeat:*` pattern saved | Nothing extra |
| **YouTube sync** | Scores saved (upsert per video) | Up to 3 improvement proposals |
| **Improvement Yes** | `applied:*` rule | — |
| **Improvement No** | `rejected:*` hint (won't re-propose similar) | — |

## What drafts see

`MemoryExtensions.applied_training_context()` bundles:

1. **Approved training rules** — from analytics improvements you approved
2. **Avoid / do not repeat** — draft rejections + rejected proposals
3. **Repeat when relevant** — approved draft patterns
4. **Recent video performance** — last 3 reward events

**Daily autopilot** (`!daily`) now uses the same learning context as the web agent.

## Commands

- `sync` / **Sync YouTube Analytics** — score videos, propose improvements
- Web sidebar **Yes/No** on improvements
- `yes <id>` / `no <id>` in Discord
- Draft **Yes/No** — learns instantly

## Storage

- **Runtime truth:** SQLite `training_config` + `feedback` table
- **Audit log:** `data/LEARNED.md` (human-readable, not read back automatically)

## vidIQ

Not used. Keyword/trend signal comes from **Google Trends**, **YouTube API**, and **browser browse** when needed.
