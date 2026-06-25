# Slack automations — copy/paste templates

Create at [cursor.com/automations](https://cursor.com/automations). Requires **Part 1** of `docs/SLACK_CURSOR_SETUP.md` (Cursor Slack app installed).

**Limits today:** Slack triggers only see **public** channels. Automations bill in **Max Mode**.

---

## 1. Keyword grind in #dont-blink-ops

**Trigger:** New message in channel `#dont-blink-ops`  
**Filter:** message matches `grind|ship|research|draft`

**Prompt:**

```
You are working on ProofOfProgress/proof-codex-ai (Peripheral horror Shorts).

Read data/PRIORITIES.md — only top 4 priorities.
Read the Slack message that triggered this run.

Do the requested work: commit, push, update PR.
Post a short summary in Slack when done (what changed, what blocked, next step).
```

**Tools:** Send to Slack, Read Slack channels, GitHub PR, repo `proof-codex-ai`

**Permission:** Private (your runs) or Team Visible

---

## 2. Pipeline alert follow-up

When webhook posts a failure (Part 3), you can reply in thread:

```
@cursor agent fix the automation alert in data/ALERTS.md — root cause + patch + test
```

Or automation **Trigger:** message contains `ALERT` or `pipeline failed` (if you forward alerts manually).

---

## 3. Nightly status (cron)

**Trigger:** Cron `0 7 * * *` (7:00 UTC)

**Prompt:**

```
Repo proof-codex-ai. Read data/ALERTS.md, pending drafts/improvements via web patterns in AGENTS.md.
Summarize: what's blocked, what's ready to upload, top 1 action for owner.
Keep under 12 lines. Post to #dont-blink-ops via Send to Slack.
```

**Tools:** Send to Slack, repo read

---

## 4. Upload retry after quota

**Trigger:** Manual or cron weekly

**Prompt:**

```
proof-codex-ai: retry canonical upload for draft 3 if YouTube quota allows:
python3 -m shorts_bot.production.upload_canonical_cli --draft-id 3 --video data/production/draft_3/final_short_v21_cctv.mp4
Report result in Slack. Do not batch QA uploads (YPP_SAFE_MODE).
```

---

## Owner vs agent

| Owner | Agent |
|-------|-------|
| Install Slack app, Link Account, webhook URL | Code, test, commit, PR |
| Approve Slack MCP in workspace | Post updates when MCP authed |
| Create automations in dashboard | Run on trigger |
