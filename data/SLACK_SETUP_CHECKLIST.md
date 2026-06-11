# Slack setup checklist — do once (~10 min)

Owner: you (OAuth). Cloud Agent cannot finish Slack auth without you.

- [ ] Install Cursor Slack app — [dashboard Integrations](https://cursor.com/dashboard?tab=integrations)
- [ ] Link **your** Cursor account in Slack (`@cursor help` → Link Account)
- [ ] Create `#dont-blink-ops` (public) → `/invite @cursor`
- [ ] `@cursor settings` → default repo `ProofOfProgress/proof-codex-ai`
- [ ] Routing rules: `shorts` / `dont-blink` → same repo
- [ ] Cursor Marketplace → Slack MCP → Connect (Desktop)
- [ ] Slack admin approves MCP if prompted
- [ ] Test: `@cursor read docs/SLACK_CURSOR_SETUP.md and reply OK`

**Night grind prompt (copy/paste):**

```
@cursor agent take 2h on proof-codex-ai — finish first Don't Blink Short (ai_video I2V),
horror VO, upload metadata. Commit + update PR. Post progress in this thread.
```
