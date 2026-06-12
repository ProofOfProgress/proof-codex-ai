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

1. In Slack, create a **public** channel: `#peripheral-ops` (you must be allowed to create channels)
2. Add Cursor to the channel — **pick one** (if `/invite @cursor` says *Sorry, you can't perform this action*, use B or C):
   - **A:** `/invite @cursor`
   - **B:** Channel name (top) → **Integrations** tab → **Add an app** → search **Cursor** → Add
   - **C:** Skip invite — in a **public** channel, type `@cursor help` (app may join on first mention if already installed workspace-wide)
3. **Or use DM:** open a direct message with **Cursor** (Apps sidebar) → `@cursor help` — no channel invite needed
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
| `/invite @cursor` → *Sorry, you can't perform this action* | Slack permissions — not Cursor. **Fix:** (1) Install Cursor from [dashboard Integrations](https://cursor.com/dashboard?tab=integrations) first. (2) Use channel **Integrations → Add app → Cursor**. (3) Or DM Cursor directly. (4) Ask **workspace owner** to install/approve the app or let members add apps to channels. |
| Reply from **GitHub APP** + “Access denied… Copilot” | **Wrong bot.** That is GitHub Copilot in Slack, not Cursor. Use **`@cursor`** (Cursor app), not `@GitHub` / `@GitHub Copilot`. Install Cursor separately: [Integrations → Slack](https://cursor.com/dashboard?tab=integrations). |
| Two apps in Slack | **Cursor** = Cloud Agents for this repo. **GitHub** = PR previews + optional Copilot agent (needs paid Copilot + org policy). They are not interchangeable. |
| @cursor ignores me | Did you **Link Account** on `@cursor help`? Dashboard connect alone is not enough. |
| Wrong repo | `@cursor settings` or say `proof-codex-ai` in the message |
| Webhook test fails | Regenerate webhook URL; check Secret name is exactly `SLACK_WEBHOOK_URL` |
| Checklist still shows ○ for @cursor | Add `SLACK_CURSOR_LINKED=true` to Secrets after Link Account |

### Correct test message

In `#peripheral-ops` (after `/invite @cursor`):

```
@cursor help
```

Then Link Account if prompted. Then:

```
@cursor agent in proof-codex-ai, reply OK
```

Do **not** use `@Cursor alphabeta` as the app name — `alphabeta` is just text in your prompt if needed.

Full technical doc: `docs/SLACK_CURSOR_SETUP.md`
