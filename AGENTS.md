# AGENTS.md

## Cursor Cloud specific instructions

### Project overview

**Shorts Bot** — Jenny Hoyos strategist CLI for faceless Shorts. Course KB in `course/files/` (01–09) + `course/verbatim/`. Free-first stack: CapCut, YouTube Audio Library, Canva free. API LLMs + future Playwright for CapCut.

### Services

Install: `bash scripts/install.sh`

Web UI (recommended):

```bash
python3 -m shorts_bot.web
# http://localhost:8080
```

CLI:

```bash
python3 -m shorts_bot
```

Set `OPENAI_API_KEY` for full conversational mode. Quick setup: `bash scripts/set-openai-key.sh` or add `OPENAI_API_KEY` to Cursor secrets (auto-synced via `scripts/sync_secrets.py` on start). See `docs/CHAT_TONIGHT.md`. Without it, offline command mode still works (`help`, `draft`, `pending`, etc.).

### Lint / test

No linter configured. Smoke checks:

```bash
pip install -r requirements.txt
python -m compileall -q shorts_bot
python -m pytest tests/ -q
```

### Data

SQLite at `data/shorts_bot.db` (gitignored). Stores drafts, approvals, rejections, chat history.

### Course

Jenny Hoyos course is in `course/`. Router picks files 01–09 per user message. Offline: `course <question>` and `free tools` commands.

### Reward & self-training

- `shorts_bot/rewards/` — score videos (swipe-away, retention) → reward/punish
- `shorts_bot/training/` — improvement proposals with pros/cons; user Yes/No in web UI
- POST `/api/score` to record metrics and auto-propose improvements

### YouTube Analytics (official API)

1. Enable YouTube Analytics API + YouTube Data API v3 in Google Cloud
2. Set `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` in `.env`
3. One-time OAuth: `python3 -m shorts_bot.youtube.auth_cli` (token → `data/youtube_token.json`)
4. Web UI: **Sync YouTube Analytics** or POST `/api/youtube/sync`
5. User approves improvements via **Yes/No** in sidebar

Home setup: `docs/RUN_AT_HOME.md` (master). YouTube: `docs/TOMORROW.md`. OpenAI: `docs/CHAT_TONIGHT.md`. Health: `bash scripts/doctor.sh`.

**Live login check:** `python3 -m shorts_bot.login_status` or `GET /api/login-status`. **Open remaining browser logins:** `python3 -m shorts_bot.login_handoff --all-remaining` (Desktop tab).

Smart chat (no OpenAI): `dev:`, `build:`, `sync`, `pending`, `yes <id>` via `BotOperations.chat`.

### Discord

- `DISCORD_BOT_TOKEN` — required to connect bot
- `DISCORD_OWNER_ID` — optional; bot remembers last DM user in `data/discord_prefs.json`
- Run: `python3 -m shorts_bot.discord_bot` or `bash scripts/run-all.sh`
- **DMs:** type normally (no `!` prefix). Servers: `!help`, `!chat`, `/status` slash commands
- Extra: `!ping`, `!learned`, `!rewards`, `!briefing`

### Dev queue

Web **Dev queue** panel or `!dev title | description` — user Yes/No before coding tasks run. Approved items append to `data/LEARNED.md`.

### Next phases

CapCut Playwright operator.

### Git / PR policy (user does minimal work)

Cloud agents **merge their own PRs** when ready. Do not wait for the user to click merge.

**Before merging:**
1. `git fetch origin main`
2. Resolve merge conflicts on the feature branch if needed
3. `python3 -m pytest tests/ -q` must pass
4. `gh pr view <N> --json mergeable,mergeStateStatus` → must be `MERGEABLE` and `CLEAN`

**Merge (no user action required):**
```bash
gh pr merge <PR_NUMBER> --repo ProofOfProgress/proof-codex-ai --merge --delete-branch
git checkout main && git pull origin main
```

**After merging:** confirm with `gh pr view <N> --json state` → `MERGED`.

The environment has `gh` authenticated. Merge permission works; closing stale PRs may require the user (optional cleanup only).
