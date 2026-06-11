# Slack ↔ Cursor — setup for long study sessions

**Goal:** Message from Slack → Cloud Agent runs → replies in Slack (while you're away from the IDE).

There are **two** official Slack integrations. Use **both** for the full loop.

| Integration | Direction | Use for |
|-------------|-----------|---------|
| **@cursor Slack app** | You → Agent → Slack thread | Start work, follow-ups, PR links, status |
| **Slack MCP** | Agent → Slack (search/send) | Agent posts updates, reads threads while grinding |

---

## Part 1 — @cursor bot (main loop) — ~5 min

This is the big one: **`@cursor fix X`** in Slack starts a Cloud Agent; it replies in the same thread.

### A. Workspace install (you or admin)

1. Open [cursor.com/dashboard → Integrations → Slack](https://cursor.com/dashboard?tab=integrations)
2. Click **Connect** → install **Cursor** into your Slack workspace
3. Back in Cursor dashboard:
   - Connect **GitHub** (repo: `ProofOfProgress/proof-codex-ai`)
   - Set **default repository** to this repo
   - Enable **usage-based pricing** (Cloud Agents are metered)
   - Confirm **Cloud Agent privacy** settings (Legacy Privacy Mode blocks Cloud Agents)

### B. Link *your* Cursor account (required per user)

1. In Slack, invite the Cursor app to a channel: `/invite @cursor`
2. Mention: `@cursor help`
3. Click **Link Account** when Slack prompts → OAuth to Cursor
4. Repeat if you use Slack on phone — same account

**Without this step, @cursor will not run agents for you.**

### C. Channel for Don't Blink / study sessions

Create a public channel, e.g. `#dont-blink-ops` (public required for channel defaults).

In that channel:

```
@cursor settings
```

Set **default repository** → `ProofOfProgress/proof-codex-ai` (or your fork).

### D. Routing rule (optional, saves typing)

Dashboard → **Cloud Agents** → **Routing rules**:

| Keyword | Target repo |
|---------|-------------|
| `shorts` | `ProofOfProgress/proof-codex-ai` |
| `dont-blink` | `ProofOfProgress/proof-codex-ai` |
| `horror` | `ProofOfProgress/proof-codex-ai` |

Then from Slack:

```
@cursor take 2h — research horror hooks and grind draft #2 to ai_video
```

### E. Commands you'll use at night / away from desk

| Say in Slack | What happens |
|--------------|----------------|
| `@cursor [prompt]` | Start agent (or follow-up in existing thread) |
| `@cursor agent [prompt]` | **New** agent in this thread (don't mix with old run) |
| `@cursor list my agents` | See what's still running |
| `@cursor settings` | Channel defaults |
| ⋯ on agent message → **Add follow-up** | Steer without @cursor when multiple agents exist |

**Important:** Plain replies **without** `@cursor` do **not** trigger the agent. Always `@cursor` or use ⋯ Add follow-up.

### F. Long study session pattern

```
@cursor agent take 2h on proof-codex-ai — deep research jumpscare Shorts SEO,
finish mirror-blink video with ai_video I2V, commit and update PR. Report in thread every major step.
```

Agent will:
- ⏳ react while running
- Post updates in thread
- ✅ + PR link when done
- You can `@cursor add tests` next morning as follow-up

---

## Part 2 — Slack MCP (agent posts *to* Slack) — ~3 min

Lets **AlphaBeta001 / Cloud Agents** search channels, read threads, and **send messages** from inside a run.

### A. Cursor Desktop (your machine)

1. [Cursor Marketplace → Slack](https://cursor.com/marketplace/slack) → **Add to Cursor**
2. **Settings → MCP → Slack** → **Connect** → complete OAuth
3. Slack **workspace admin** may need to **approve** the MCP app

### B. Cloud Agent VM (this environment)

Slack MCP shows **`needsAuth`** until you connect from Cursor:

1. Same Cursor account → Dashboard → **Integrations** → enable **Slack MCP** for Cloud Agents
2. Or per-run: [cursor.com/agents](https://cursor.com/agents) → MCP dropdown → enable Slack

After auth, agents can call Slack tools (post to `#dont-blink-ops`, read your thread, etc.).

### C. Repo MCP config (optional local hint)

If you use project MCP config, hosted OAuth is preferred:

```json
{
  "mcpServers": {
    "slack": {
      "url": "https://mcp.slack.com/mcp",
      "auth": {
        "CLIENT_ID": "3660753192626.8903469228982"
      }
    }
  }
}
```

Cloud Agents use **dashboard** MCP config, not only repo files.

---

## Part 3 — Automations (hands-off, optional)

Dashboard → **Cloud Agents** → **Automations**:

- **Trigger:** New message in `#dont-blink-ops` matching regex e.g. `grind|research|ship`
- **Action:** Run agent + **Send to Slack** with summary

Use when you want to post a normal message (no `@cursor`) and still kick work. Separate from `@cursor` mentions.

---

## What works / what doesn't

| Works | Doesn't |
|-------|---------|
| `@cursor` starts Cloud Agent | Every Slack message auto-triggers agent |
| Thread follow-ups with `@cursor` | Team uses @cursor without linking own account |
| Agent replies + PR in thread | Private-channel automation triggers (public only) |
| Slack MCP send/search when authed | Slack MCP in VM without your OAuth |
| 2h work budgets via natural language | Guaranteed DM on every web-started agent |

---

## Quick test (after setup)

In `#dont-blink-ops`:

```
@cursor in proof-codex-ai, read docs/SLACK_CURSOR_SETUP.md and confirm Slack is wired. Reply with OK + what you can do from Slack.
```

You should see ⏳ → agent message → ✅.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Link Account" loop | Dashboard → Cloud Agents → Unlink Slack → re-link |
| Wrong repo | `@cursor settings` in channel or include `proof-codex-ai` in prompt |
| Agent silent | Use `@cursor agent` for new thread; check `list my agents` |
| MCP tools empty | Auth Slack MCP in Desktop + admin approve |
| Upload blocked | Separate issue — `upload_guard` still 1/day unless you change `.env` |

---

## Links

- [Cursor Slack integration](https://cursor.com/docs/integrations/slack)
- [Cloud Agents](https://cursor.com/docs/cloud-agent)
- [Slack marketplace — Cursor](https://slack.com/marketplace/A08SKDT6QUW)
