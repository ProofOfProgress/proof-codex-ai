# Self-learning model

Don't Blink learns from **your decisions** and **YouTube performance** — then injects rules into the next draft and strategist chat.

## Loop

```
YouTube sync (auto every 12h) → RewardEngine → improvement proposal (max 3/sync)
Safe hook/retention proposals → auto-Yes (no tap)
Reflective self-training (System 2) → episodes + rule confidence + promote to agent memory
Draft Yes/No / auto-approve → immediate avoid/repeat + improvement proposal + episode
Applied rules + reflections → DraftGenerator + ShortsBotAgent (refreshed each message)
```

See `docs/AUTONOMOUS_SELF_TRAINING_RESEARCH.md` for the full architecture.

## What runs without you

| Step | Automation |
|------|------------|
| **Analytics sync** | Every `AUTO_ANALYTICS_SYNC_INTERVAL_HOURS` (Discord + web background) |
| **Hook/retention improvements** | Auto-approved when category is safe (no login/payment/niche pivot) |
| **Daily Short** | `AUTO_DAILY_ENABLED` at `AUTO_DAILY_HOUR` UTC |
| **Unlisted upload** | Flips to public after `AUTO_PUBLISH_HOURS` |
| **Auto-approved draft** | `learn_from_draft` → `repeat:*` immediately |
| **Dev tasks (no login)** | Auto-approved → `data/DEV_QUEUE.md` |

## What you still approve (if any)

| Input | What happens | Manual when |
|-------|--------------|-------------|
| **Reject draft** | `avoid:*` rule | You reject manually |
| **Risky improvement** | Stays pending | strategy / login / payment wording |
| **Login/payment dev task** | Stays pending | `devyes` or web UI |

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
- **Episodic memory:** `learning_episodes` + `rule_confidence` tables
- **Upload attribution:** `upload_events.active_rules_json` snapshot at publish
- **Audit log:** `data/LEARNED.md` (human-readable; excerpt now injected into training context)

## vidIQ

Not used. Keyword/trend signal comes from **Google Trends**, **YouTube API**, and **browser browse** when needed.
