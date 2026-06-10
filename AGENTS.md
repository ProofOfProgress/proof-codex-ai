# AGENTS.md

## Cursor Cloud specific instructions

### Project overview

**Shorts Bot** — Jenny Hoyos strategist CLI for faceless Shorts. Course KB in `course/files/` (01–09) + `course/verbatim/`. **Paid autopilot stack (required by default):** Gemini + **Resemble** voice clone + **TurboScribe Whale** + **stick figure frames** (ChainsFR-style: figure acts each beat, minimal scene per timestamp) + ffmpeg (no CapCut/Higgsfield). Default `VISUAL_STYLE=stickfigure`. See `docs/CHAINSFR_RESEARCH.md`, `docs/PAID_STACK_SETUP.md`, `docs/SHORTS_ALIGNMENT.md`, `docs/PRODUCTION_RESEARCH.md`, `docs/HEALTH_NICHE_RESEARCH.md` (10 high-RPM health/mental health niches). (methods, variety, sync, QC).

**Channel mission:** loyal subscribers who come back because content **actually helps** — not viral one-offs. **TikTok account planned later** — no TikTok automation until user says go (`data/operating_rules_seed.md`).

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

**Chief Manager (multi-agent):** `python3 -m shorts_bot.agents.cli` — delegates Gemini specialists. Say `take 1h to plan cosy shorts` or `[30m] score topics` to set work budget before reply. Web: `POST /api/manager/run`, poll `GET /api/manager/jobs/{id}`. See `docs/AGENT_MANAGER.md`. Discord optional — CLI/web preferred.

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

**Deep research:** `research <topic>` / `deep research <topic>` — web browse, Google Trends, YouTube competitors, browser fallback. vidIQ off by default. See `docs/DEEP_RESEARCH.md`, `docs/BROWSER.md`.

**Self-learning:** Draft reject → immediate `avoid:*` rules; sync → reward proposals (max 3); safe improvements auto-approved; agent training context refreshes each chat. See `docs/SELF_LEARNING.md`.

**Automation (default on):** Background analytics sync, auto-Yes on safe improvements, scheduled `!daily`, unlisted→public after 24h, quality gate + **YPP upload guard** before upload, **light comment auto-reply** (serious → `comments pending`). Login/payments still manual. See `docs/COMMENTS.md`, `docs/YPP_ANTI_SHADOWBAN.md`. Config: `YPP_SAFE_MODE`, `MAX_UPLOADS_PER_24H`, `AUTO_DAILY_ENABLED` in `.env`.

**Browser:** Playwright Chromium + `data/browser_profile/`. Discord/chat: `browse <url>`, `browser open vidiq`. Agent tools: `browse_web`, `open_browser`. `python3 -m shorts_bot.browser.cli status`. See `docs/BROWSER.md`.

### Course

Jenny Hoyos course is in `course/`. Router picks files 01–09 per user message. Offline: `course <question>` and `free tools` commands.

### Reward & self-training

- `shorts_bot/rewards/` — score videos (swipe-away, retention) → reward/punish
- `shorts_bot/training/` — improvement proposals with pros/cons; user Yes/No in web UI
- POST `/api/score` to record metrics and auto-propose improvements

### YouTube Analytics (official API)

1. Enable YouTube Analytics API + YouTube Data API v3 in Google Cloud
2. Set `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` in `.env`
3. One-time OAuth: `python3 -m shorts_bot.youtube.auth_cli` (token → `data/youtube_token.json`). For API uploads add `YOUTUBE_OAUTH_UPLOAD=1`.
4. Web UI: **Sync YouTube Analytics** or POST `/api/youtube/sync`
5. **Upload fallback:** if token lacks `youtube.upload`, use `python3 -c "from pathlib import Path; from shorts_bot.youtube.studio_upload import upload_pack_via_studio; print(upload_pack_via_studio(Path('data/production/draft_N')))"` — may need Desktop browser if Google shows “Verify it’s you”.
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

Web **Dev queue** panel or `!dev title | description` — safe tasks auto-approve to `data/DEV_QUEUE.md`; login/payment tasks need `devyes`. Approved items also append to `data/LEARNED.md`.

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
