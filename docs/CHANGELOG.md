# Changelog

## 0.6.0 — full stack (login is only bottleneck)

- UI: setup checklist, hero Yes/No card, reward detail cards
- Discord: notify all DM users + DISCORD_NOTIFY_IDS, scheduled 8:30 briefing, `!notify`
- Smart chat: `dev:`, `build:`, `sync`, `pending`, `yes/no` without OpenAI
- Dev queue tool for agent; dev task dedupe
- `/api/checklist`, Docker compose, docs/RUN_AT_HOME.md

## 0.5.0 — overnight polish

- Discord: natural DM chat (no `!` prefix), slash commands, rich embeds
- Discord: remembers your DM for morning briefings without `DISCORD_OWNER_ID`
- New commands: `!ping`, `!learned`, `!rewards`
- Web: toasts, favicon, expanded `/health`, copy learned rules
- Duplicate improvement proposals collapsed automatically
- Scripts: `backup.sh`, `stop.sh`, `Makefile`, GitHub Actions CI
- Docs: `QUICKSTART.md`
