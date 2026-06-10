# AGENTS.md

## Cursor Cloud specific instructions

### Project overview

**Shorts Bot** — Jenny Hoyos strategist CLI for faceless Shorts. Course KB in `course/files/` (01–09) + `course/verbatim/`. **Paid autopilot stack:** Gemini + Resemble voice clone + TurboScribe Whale + ffmpeg (no CapCut). See `docs/PAID_STACK_SETUP.md`.

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

Set `GEMINI_API_KEY` (free, preferred) or `OPENAI_API_KEY` for full conversational mode. Keys sync via `scripts/sync_secrets.py` on start. See `docs/CHAT_TONIGHT.md`. Without either, offline command mode still works (`help`, `draft`, `pending`, etc.).

### Lint / test

No linter configured. Smoke checks:

```bash
pip install -r requirements.txt
python -m compileall -q shorts_bot
python -m pytest tests/ -q
```

### Data

SQLite at `data/shorts_bot.db` (gitignored). Stores drafts, approvals, rejections, chat history.

**Agent memory (persistent):** operating rules / preferences / facts in `agent_memories` table; exported to `data/MEMORY.md`. Seeded from `data/operating_rules_seed.md` on first run. Injected into strategist + draft prompts; restored chat context on agent startup (`memory_chat_context_limit`, default 24). Commands: `remember <text>`, `memory`, `forget <id>` (Discord: `!remember`, `!memory`, `!forget`). CLI: `python3 -m shorts_bot.memory.memory_cli list`. See `docs/AGENT_MEMORY.md`.

**Deep research:** `research <topic>` / `deep research <topic>` — web browse, Google Trends (YouTube search via `pytrends`), YouTube competitors, vidIQ keywords, Jenny synthesis. `VIDIQ_API_KEY` or `login_handoff --only vidiq`. See `docs/DEEP_RESEARCH.md`, `docs/VIDIQ_SETUP.md`.

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

- `DISCORD_BOT_TOKEN` — required; enable **Message Content Intent** in Developer Portal
- `DISCORD_OWNER_ID` — numeric user ID (`!myid`); owner can chat in servers without `@`
- Run: `bash scripts/discord-bot.sh` or `python3 -m shorts_bot.discord_bot`
- **DMs:** type normally. **Servers:** `!daily`, `@Bot message`, or slash `/daily`
- API pipeline: `daily`, `apply brand`, `finish video`, `research` — see `docs/DISCORD_CONTROL.md`

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
