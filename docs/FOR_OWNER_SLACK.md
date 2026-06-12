# Slack setup — for you (~10 minutes)

No coding. Two things: **@cursor** (you message agents from your phone) and **webhook** (bot posts alerts to Slack).

Open the web UI → **Slack** tab for live progress, or run `bash scripts/slack-setup.sh`.

Suggested channel: **#peripheral-ops** (public).

---

## Part 1 — @cursor (main loop) — ~5 min

### Step 1 — Install the app

1. Open [cursor.com/dashboard → Integrations → Slack](https://cursor.com/dashboard?tab=integrations)
2. Click **Connect** and install Cursor in your Slack workspace
3. Connect **GitHub** → repo `ProofOfProgress/proof-codex-ai`

### Step 2 — Channel + link your account

1. In Slack, create a **public** channel: `#peripheral-ops`
2. Type: `/invite @cursor`
3. Type: `@cursor help`
4. Click **Link Account** when Slack asks (OAuth to Cursor — required)

### Step 3 — Default repo

In `#peripheral-ops`, type:

```
@cursor settings
```

Set default repository to **proof-codex-ai**.

### Step 4 — Tell the bot you're done

In **Cursor → Secrets**, add:

```
SLACK_CURSOR_LINKED=true
```

Then run `bash scripts/install.sh` on the machine running the bot.

### Step 5 — Test

Paste in Slack:

```
@cursor agent in proof-codex-ai, read docs/FOR_OWNER_SLACK.md and reply OK
```

You should see ⏳ then a reply in the thread.

---

## Part 2 — Webhook (pipeline alerts) — ~3 min

So the bot can post to Slack when something fails or uploads complete — without you opening the web UI.

1. Slack → **Apps** → search **Incoming Webhooks** → **Add to Slack**
2. Pick channel **#peripheral-ops** → **Allow**
3. Copy the URL (starts with `https://hooks.slack.com/services/...`)
4. **Cursor → Secrets** → add `SLACK_WEBHOOK_URL` = that URL
5. Run `bash scripts/install.sh`
6. Test:
   - Web UI → **Slack** tab → **Send test message**
   - Or terminal: `python3 -m shorts_bot.integrations test`

You should see a message in the channel: *Peripheral bot connected.*

---

## Part 3 — Optional extras

| What | Where |
|------|--------|
| Slack MCP (agents post while working) | [Cursor Marketplace → Slack](https://cursor.com/marketplace/slack) → Connect |
| Automations (subscriber count, daily post) | [cursor.com/automations](https://cursor.com/automations) — you already set these up |
| Night grind prompt | `@cursor agent take 2h on proof-codex-ai — finish draft 3, commit, update PR` |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| @cursor ignores me | Did you **Link Account**? Not just install the app. |
| Wrong repo | `@cursor settings` or say `proof-codex-ai` in the message |
| Webhook test fails | Regenerate webhook URL; check Secret name is exactly `SLACK_WEBHOOK_URL` |
| Checklist still shows ○ for @cursor | Add `SLACK_CURSOR_LINKED=true` to Secrets after Link Account |

Full technical doc: `docs/SLACK_CURSOR_SETUP.md`
