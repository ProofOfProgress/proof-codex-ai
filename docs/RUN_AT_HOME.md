# Run at home — complete guide

Everything works **without** OpenAI or Google until you're ready. One-time login steps need you; day-to-day, the only manual video step is **Private → Public** in YouTube Studio.

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

## 3. Channel brand: Soft Continuity

- **Vibe:** self-help Shorts, friendly, subtly uncanny (oracle tone — never explicit horror)
- **Paste into YouTube:** `docs/YOUTUBE_CHANNEL_SETUP.md`
- **Banner:** open `channel/brand/assets/banner.svg` → Canva or screenshot
- **Starter scripts:** `python3 scripts/seed_starter_drafts.py` → approve in web UI

## 4. Production pipeline (automated except publish)

| Step | Who | Notes |
|------|-----|--------|
| Ideas + script draft | Bot | Jenny course + your niche |
| Approve / reject draft | You | Web **Yes/No** |
| CapCut edit + export | Bot | Uses `channel/brand/capcut_style.md` |
| Upload to YouTube | Bot | Always **Private** first |
| **Private → Public** | **You** | Only manual step per video (~30 sec) |
| Sync analytics + learn | Bot | Web **Sync**; you Yes/No improvements |

## 5. What works immediately (no login)

- Web chat at http://localhost:8080 (type normally)
- `draft sleep tips` — script drafts
- `dev: polish UI | make cards glow` — coding task queue
- Web **Yes/No** approvals (improvements, drafts, dev)
- Reward learning loop (after you have video data)
- Jenny course routing offline

## 6. What needs you once (login only)

| Step | Time | Doc |
|------|------|-----|
| Google API keys | ~10 min | docs/TOMORROW.md |
| YouTube OAuth once | ~2 min | `python3 -m shorts_bot.youtube.auth_cli` |
| OpenAI API key (optional) | ~2 min | docs/CHAT_TONIGHT.md |

## 7. Morning briefing

Open **http://localhost:8080** or `GET /api/briefing` for the daily checklist.

Optional: link **Slack + @cursor** for remote steering — see **docs/SLACK_CURSOR_SETUP.md**.

## 8. Self-learning flow

1. Bot uploads approved Shorts as **Private** (or you flip older uploads to Public when ready)
2. After Google login: tap **Sync YouTube Analytics** (web)
3. Bot scores videos → proposes up to **3 improvements** with pros/cons
4. Tap **Yes** or **No** (one tap on web, or `yes 3` / `no 3` in chat)
5. Approved rules → `data/LEARNED.md` + better future drafts

## 9. Dev / coding requests

**Web chat:** `build: add export button for drafts`

**Web:** Dev queue panel → describe → Yes to approve

**Future:** approved dev tasks are picked up by the cloud agent.

## 10. Troubleshooting

```bash
bash scripts/doctor.sh    # what's missing
bash scripts/stop.sh      # stop services
bash scripts/backup.sh    # backup database
make test                 # 37+ tests
```

## 11. Local hosting (Docker, optional)

```bash
docker compose up --build
```

Same UI at http://localhost:8080 — data in `./data`.
