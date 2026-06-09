# Run at home — complete guide

Everything works **without** OpenAI or Google until you're ready. Only login steps need you.

## 1. Pull latest

```bash
cd proof-codex-ai   # your project folder
git pull
bash scripts/install.sh
```

## 2. Start

```bash
bash scripts/run-all.sh
```

| Service | URL / access |
|---------|----------------|
| Web dashboard | http://localhost:8080 |
| Discord | DM the bot or `!help` in server |

## 3. What works immediately (no login)

- Discord chat in DM (type normally, no `!`)
- `!draft sleep tips` — script drafts
- `dev: polish UI | make cards glow` — coding task queue
- Web **Yes/No** approvals (improvements, drafts, dev)
- Reward learning loop (after you have video data)
- Jenny course routing offline

## 4. What needs you once (login only)

| Step | Time | Doc |
|------|------|-----|
| Discord bot token | done if bot replies | docs/MORNING.md |
| Google API keys | ~10 min | docs/TOMORROW.md |
| YouTube OAuth once | ~2 min | `python3 -m shorts_bot.youtube.auth_cli` |
| OpenAI API key (optional) | ~2 min | docs/CHAT_TONIGHT.md |

## 5. Discord — text you + others

Anyone who **DMs the bot** is auto-remembered for morning messages.

To add more people without them DMing first:

```
DISCORD_NOTIFY_IDS=123456789012345678,987654321098765432
```

Morning briefing runs at **8:30** (change in `.env`):

```
DISCORD_BRIEFING_HOUR=8
DISCORD_BRIEFING_MINUTE=30
```

Manual ping: `!notify` in Discord.

## 6. Self-learning flow

1. Upload Shorts on YouTube
2. After Google login: tap **Sync YouTube Analytics** (web) or `!sync` (Discord)
3. Bot scores videos → proposes up to **3 improvements** with pros/cons
4. Tap **Yes** or **No** (one tap, web or `!yes 3` / `!no 3`)
5. Approved rules → `data/LEARNED.md` + better future drafts

## 7. Dev / coding requests

**Discord DM:** `build: add export button for drafts`

**Web:** Dev queue panel → describe → Yes to approve

**Future:** approved dev tasks are picked up by the cloud agent.

## 8. Troubleshooting

```bash
bash scripts/doctor.sh    # what's missing
bash scripts/stop.sh      # stop services
bash scripts/backup.sh    # backup database
make test                 # 37+ tests
```

## 9. Local hosting (Docker, optional)

```bash
docker compose up --build
```

Same UI at http://localhost:8080 — data in `./data`.
