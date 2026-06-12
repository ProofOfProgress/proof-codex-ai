# Slack setup checklist — do once (~10 min)

Owner completes OAuth in browser. Cloud Agent cannot finish Slack auth without you.

Run: `bash scripts/slack-setup.sh`

## @cursor (remote agents)

- [ ] Install Cursor Slack app — [dashboard Integrations](https://cursor.com/dashboard?tab=integrations)
- [ ] Connect GitHub → `ProofOfProgress/proof-codex-ai`
- [ ] Create `#peripheral-ops` (public) → `/invite @cursor`
- [ ] `@cursor help` → **Link Account** (OAuth)
- [ ] `@cursor settings` → default repo `proof-codex-ai`
- [ ] Cursor Secrets → `SLACK_CURSOR_LINKED=true` → `bash scripts/install.sh`
- [ ] Routing rules: `shorts` / `peripheral` / `dont-blink` → same repo
- [ ] Test: `@cursor read docs/FOR_OWNER_SLACK.md and reply OK`

## Slack MCP (agents post while working)

- [ ] Cursor Marketplace → Slack MCP → Connect (Desktop)
- [ ] Dashboard → Integrations → Slack MCP for Cloud Agents
- [ ] Slack admin approves MCP if prompted

## Option A — Email into Slack (no bot token) **recommended if /invite fails**

- [ ] `#peripheral-ops` → Integrations → **Email** → copy address
- [ ] Google → App Password for ops Gmail
- [ ] Cursor Secrets → `SLACK_CHANNEL_EMAIL`, `GMAIL_SMTP_USER`, `GMAIL_SMTP_APP_PASSWORD`
- [ ] Optional: `SLACK_POST_MODE=email` to skip bot/webhook
- [ ] `bash scripts/install.sh`
- [ ] `python3 -m shorts_bot.integrations test` → email appears in channel

Guide: `docs/FOR_OWNER_SLACK_EMAIL.md`

## Gmelius + Slack for Gmail (optional — browser, not bot SMTP)

- [ ] Gmelius Chrome extension installed (Desktop Chrome)
- [ ] Sign in Gmelius with ops Gmail (2FA on phone)
- [ ] app.gmelius.com → Integrations → Slack → peripheralorg → `#peripheral-ops`
- [ ] `/invite @gmelius` in channel if needed
- [ ] [Slack for Gmail](https://workspace.google.com/marketplace/app/slack_for_gmail/533288507123) → Install (Gmail sidebar — **won’t** show under Slack Apps)

Guide: `docs/FOR_OWNER_GMELIUS_GMAIL.md`

## Webhook (pipeline alerts — alternative)

- [ ] Slack → Incoming Webhooks → add to `#peripheral-ops`
- [ ] Cursor Secrets → `SLACK_WEBHOOK_URL`
- [ ] `bash scripts/install.sh`
- [ ] `python3 -m shorts_bot.integrations test` → message in channel

## Night grind (copy/paste)

```
@cursor agent take 2h on proof-codex-ai — finish Peripheral Short pipeline,
horror VO + vision QC, upload when quota allows. Commit + PR. Post progress here.
```
