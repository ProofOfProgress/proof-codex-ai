# AGENTS.md

## Owner (read first)

- **Not a developer** — explain in plain English; give exact steps ("say `!daily` in Discord"), not code tours.
- **North star (#1 priority):** self-learning, fully self-improving, self-posting, self-operating AI YouTube channel that makes **a lot of money**. Every action should move toward full autopilot revenue. Details in `data/operating_rules_seed.md` (Owner + North star sections).
- **Deprioritize** refactors, docs-for-docs-sake, and features that do not advance autopilot or revenue.
- **Top 4 only:** see `data/PRIORITIES.md` — work only on those four until reassessed; update the file when priorities shift.

## Cursor Cloud specific instructions

### Project overview

**Shorts Bot** — Jenny Hoyos strategist CLI for faceless Shorts. Course KB in `course/files/` (01–09) + `course/verbatim/`. **Paid autopilot stack (required by default):** **Gemini** (chat + audio transcript + vision QC) + **Resemble** voice + **stick figure frames**. Keys sync from Cursor secrets via `bash scripts/install.sh` — no hand-editing `.env`. (ChainsFR-style: figure acts each beat, minimal scene per timestamp) + ffmpeg (no CapCut/Higgsfield). Default `VISUAL_STYLE=stickfigure`. See `docs/CHAINSFR_RESEARCH.md`, `docs/PAID_STACK_SETUP.md`, `docs/SHORTS_ALIGNMENT.md`, `docs/PRODUCTION_RESEARCH.md`, `docs/HEALTH_NICHE_RESEARCH.md`, `docs/AI_VIDEO_PROMPTING_RESEARCH.md` (I2V prompts: `ai_video_prompts_cli`; pack export: `video_prompt_pack_cli --draft-id N --hybrid`). (methods, variety, sync, QC).

**Channel mission:** loyal subscribers who come back because content **actually helps** — not viral one-offs. **TikTok account planned later** — no TikTok automation until user says go (`data/operating_rules_seed.md`).

### Services

Install: `bash scripts/install.sh`

**Cursor Cloud Agent secrets:** add keys in Cursor → your cloud agent → Secrets (same names as below). Run `bash scripts/install.sh` on the VM to sync into `.env`. See secret checklist in `docs/CURSOR_SECRETS.md`.

Web UI (recommended):

```bash
python3 -m shorts_bot.web
# http://127.0.0.1:8080 (binds localhost by default)
```

Set `WEB_API_TOKEN` in `.env` to require Bearer token on mutating `/api/*` routes (UI auto-injects when served from `/`).

CLI:

```bash
python3 -m shorts_bot
```

Set `GEMINI_API_KEY` (free, preferred) or `OPENAI_API_KEY` for full conversational mode. Keys sync via `scripts/sync_secrets.py` on start. See `docs/CHAT_TONIGHT.md`. Without either, offline command mode still works (`help`, `draft`, `pending`, etc.).

**Chief Manager + underlings:** `python3 -m shorts_bot.agents.cli` — you talk to the manager only; research underlings work behind the scenes (`MANAGER_WORK_PRIORITY=research` by default). Say `take 1h to research cosy topics` or just `plan this week's hooks`. Web: `POST /api/manager/run`. See `docs/AGENT_MANAGER.md`. Discord optional.

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

**Self-learning:** Draft reject → immediate `avoid:*` rules; sync → reward proposals (max 3) + **reflective self-training** (episodes, rule confidence, promote to agent memory); safe improvements auto-approved. See `docs/SELF_LEARNING.md`, `docs/AUTONOMOUS_SELF_TRAINING_RESEARCH.md`. Config: `SELF_TRAINING_ENABLED=true`.

**Automation (default on):** Background analytics sync, auto-Yes on safe improvements, scheduled `!daily`, **uploads stay unlisted** (`AUTO_PUBLISH_HOURS=0`), **Gemini vision QC** + ffmpeg QC before upload, **YouTube API upload** (no Studio Playwright). One-time: `python3 -m shorts_bot.youtube.auth_cli` (Google sign-in in system browser).

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
