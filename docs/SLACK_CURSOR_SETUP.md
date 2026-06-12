# Slack ↔ Cursor — remote ops for Peripheral

**Goal:** Run production from your phone — pipeline alerts in Slack, `@cursor` starts Cloud Agents, agents reply in thread.

Use **three** pieces (all optional but together they're the full loop):

| Piece | Direction | Use for |
|-------|-----------|---------|
| **@cursor Slack app** | You → Agent → Slack thread | Start work, follow-ups, PR links |
| **Slack MCP** | Agent → Slack (search/send) | Agent posts progress while grinding |
| **Incoming webhook** | Bot → Slack channel | Pipeline failures, upload alerts |

**Quick start:** `bash scripts/slack-setup.sh` prints the checklist.

---

## Part 1 — @cursor bot (main loop) — ~5 min

**`@cursor fix X`** in Slack starts a Cloud Agent; it replies in the same thread.

### A. Workspace install

1. [cursor.com/dashboard → Integrations → Slack](https://cursor.com/dashboard?tab=integrations)
2. **Connect** → install **Cursor** in your Slack workspace
3. Connect **GitHub** → `ProofOfProgress/proof-codex-ai`
4. Set **default repository** to this repo
5. Enable **usage-based pricing** (Cloud Agents are metered)
6. Confirm **Cloud Agent privacy** (Legacy Privacy Mode blocks Cloud Agents)

### B. Link your Cursor account (required)

1. Create public channel `#peripheral-ops` (or `#dont-blink-ops` — set `SLACK_CHANNEL_NAME`)
2. `/invite @cursor`
3. `@cursor help` → **Link Account** → OAuth to Cursor
4. `@cursor settings` → default repo `ProofOfProgress/proof-codex-ai`

**Without Link Account, @cursor will not run agents for you.**

### C. Routing rules (optional)

Dashboard → **Cloud Agents** → **Routing rules**:

| Keyword | Target repo |
|---------|-------------|
| `shorts` | `ProofOfProgress/proof-codex-ai` |
| `dont-blink` | `ProofOfProgress/proof-codex-ai` |
| `peripheral` | `ProofOfProgress/proof-codex-ai` |

### D. Commands you'll use away from desk

| Say in Slack | What happens |
|--------------|----------------|
| `@cursor [prompt]` | Start agent (or follow-up in thread you own) |
| `@cursor agent [prompt]` | **New** agent in this thread |
| `@cursor list my agents` | Running agents |
| `@cursor settings` | Channel defaults |
| ⋯ → **Add follow-up** | Steer without @cursor |

**Plain replies without `@cursor` do not trigger the agent.**

### E. Night grind (copy/paste)

```
@cursor agent take 2h on proof-codex-ai — deep research horror hooks,
finish draft #3 CCTV Short (ai_video if owner approved), vision QC, upload meta.
Commit + update PR. Post progress in this thread every major step.
```

---

## Part 2 — Slack MCP (agent posts *to* Slack) — ~3 min

Lets Cloud Agents search channels and send messages during a run.

### Cursor Desktop

1. [Cursor Marketplace → Slack](https://cursor.com/marketplace/slack) → **Add to Cursor**
2. **Settings → MCP → Slack** → **Connect** → OAuth
3. Slack workspace admin may need to **approve** the MCP app

### Cloud Agent VM

Cloud Agents use **dashboard MCP**, not repo `.cursor/mcp.json`.

1. [cursor.com/dashboard → Integrations](https://cursor.com/dashboard?tab=integrations) → enable **Slack MCP** for Cloud Agents
2. Or per run: [cursor.com/agents](https://cursor.com/agents) → MCP dropdown → Slack

Local IDE hint (optional): copy `.cursor/mcp.json.example` → `~/.cursor/mcp.json` and Connect.

---

## Part 3 — Incoming webhook (pipeline alerts) — ~2 min

The **Shorts Bot** posts automation failures and alerts to Slack without you opening the web UI.

### Setup

1. Slack → **Apps** → **Incoming Webhooks** → **Add to Slack**
2. Pick channel `#peripheral-ops` → **Allow**
3. Copy webhook URL (`https://hooks.slack.com/services/...`)
4. Add to **Cursor Secrets** as `SLACK_WEBHOOK_URL`
5. Run `bash scripts/install.sh`
6. Test:

```bash
python3 -m shorts_bot.integrations test
```

You should see: *"Peripheral bot connected. Pipeline alerts will post here."*

### Config (`.env`)

| Variable | Default | Meaning |
|----------|---------|---------|
| `SLACK_WEBHOOK_URL` | — | Incoming webhook URL |
| `SLACK_NOTIFY_ENABLED` | `true` | Master switch for webhook posts |
| `SLACK_CHANNEL_NAME` | `peripheral-ops` | Label in status/briefing only |
| `SLACK_CURSOR_LINKED` | `true` | Set after @cursor Link Account |

Alerts also land in `data/ALERTS.md` — Slack is the phone-friendly mirror.

### Verify

```bash
python3 -m shorts_bot.integrations status
curl http://localhost:8080/api/slack/status
python3 -m shorts_bot.login_status   # Slack rows in table
```

---

## Part 4 — Automations (hands-off, optional)

[cursor.com/automations](https://cursor.com/automations) — trigger agents without typing `@cursor` every time.

Examples in **docs/SLACK_AUTOMATIONS.md**:

- Keyword `grind` in `#dont-blink-ops` → run agent + post summary
- Nightly cron → check `data/ALERTS.md` + report

**Note:** Slack triggers only work on **public** channels today.

---

## Quick test (after Part 1)

```
@cursor in proof-codex-ai, read docs/SLACK_CURSOR_SETUP.md and confirm Slack is wired. Reply OK + what you can do from Slack.
```

Expect: ⏳ → agent message → ✅.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Link Account" loop | Dashboard → Cloud Agents → Unlink Slack → re-link |
| Wrong repo | `@cursor settings` or include `proof-codex-ai` in prompt |
| Agent silent | `@cursor agent` for new thread; `list my agents` |
| MCP tools empty | Auth Slack MCP in Desktop + dashboard; admin approve |
| Webhook test fails | Regenerate URL; check `SLACK_WEBHOOK_URL` in `.env` |
| Cloud Agent ignores repo mcp.json | Expected — use dashboard MCP only |

---

## Links

- [Cursor Slack integration](https://cursor.com/docs/integrations/slack)
- [Cloud Agents](https://cursor.com/docs/cloud-agent)
- [Automations](https://cursor.com/docs/cloud-agent/automations)
- [Slack marketplace — Cursor](https://slack.com/marketplace/A08SKDT6QUW)
