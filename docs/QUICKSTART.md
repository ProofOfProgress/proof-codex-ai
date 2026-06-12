# Quickstart

```bash
git pull
bash scripts/install.sh
bash scripts/doctor.sh
bash scripts/run-all.sh
```

| What | Where |
|------|--------|
| Web dashboard | http://localhost:8080 |
| Morning guide | docs/MORNING.md |
| YouTube setup | docs/TOMORROW.md |
| OpenAI chat | docs/CHAT_TONIGHT.md (optional) |
| Slack + Cursor | docs/SLACK_CURSOR_SETUP.md (optional) |

**Pipeline:** bot drafts → you approve → bot edits + uploads **Private** → you set **Public** in Studio.

## Web chat

Open **http://localhost:8080** and type normally — no special prefix needed.

## Useful chat commands

```
status    pending    briefing    learned    rewards
draft sleep tips
yes 3     no 3
dev Polish UI | make cards prettier
```

## Stop / backup

```bash
bash scripts/stop.sh
bash scripts/backup.sh
```
