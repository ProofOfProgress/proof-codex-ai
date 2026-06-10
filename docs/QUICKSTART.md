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
| Discord | `!help` in your DM or server |
| Morning guide | docs/MORNING.md |
| YouTube setup | docs/TOMORROW.md |
| OpenAI chat | docs/CHAT_TONIGHT.md (optional) |

**Pipeline:** bot drafts → you approve → bot edits + uploads **Private** → you set **Public** in Studio.

## Discord without prefix (DMs)

In a **private DM**, you can type normally — no `!` needed. The bot treats it like `!chat`.

## Useful commands

```
!status !pending !briefing !learned !rewards
!draft sleep tips
!yes 3    !no 3
!dev Polish UI | make cards prettier
```

## Stop / backup

```bash
bash scripts/stop.sh
bash scripts/backup.sh
```
