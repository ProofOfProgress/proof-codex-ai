# Slack setup checklist — do once (~10 min)

Owner completes OAuth in browser. Cloud Agent cannot finish Slack auth without you.

Run: `bash scripts/slack-setup.sh`

## @cursor (remote agents)

- [ ] Install Cursor Slack app — [dashboard Integrations](https://cursor.com/dashboard?tab=integrations)
- [ ] Connect GitHub → `ProofOfProgress/proof-codex-ai`
- [ ] Create `#dont-blink-ops` (public) → `/invite @cursor`
- [ ] `@cursor help` → **Link Account** (OAuth)
- [ ] `@cursor settings` → default repo `proof-codex-ai`
- [ ] Routing rules: `shorts` / `dont-blink` / `peripheral` → same repo
- [ ] Test: `@cursor read docs/SLACK_CURSOR_SETUP.md and reply OK`

## Slack MCP (agents post while working)

- [ ] Cursor Marketplace → Slack MCP → Connect (Desktop)
- [ ] Dashboard → Integrations → Slack MCP for Cloud Agents
- [ ] Slack admin approves MCP if prompted

## Webhook (pipeline alerts from bot)

- [ ] Slack → Incoming Webhooks → add to `#dont-blink-ops`
- [ ] Cursor Secrets → `SLACK_WEBHOOK_URL`
- [ ] `bash scripts/install.sh`
- [ ] `python3 -m shorts_bot.integrations test` → message in channel

## Night grind (copy/paste)

```
@cursor agent take 2h on proof-codex-ai — finish Peripheral Short pipeline,
horror VO + vision QC, upload when quota allows. Commit + PR. Post progress here.
```
