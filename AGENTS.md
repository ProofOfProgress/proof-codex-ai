# AGENTS.md

## Owner (read first)

- **Not a developer** — explain in plain English; give exact steps ("say `!daily` in Discord"), not code tours.
- **North star:** autonomous money-making channel. **Current focus:** **100% automation** + **better videos** (hooks, sync, vision QC, analytics learning). Top 4 only in `data/PRIORITIES.md`.
- **Deprioritize** refactors, docs-for-docs-sake, and features that do not advance autopilot or revenue.
- **Top 4 only:** see `data/PRIORITIES.md` — work only on those four until reassessed; update the file when priorities shift.
- **Do it yourself:** external setup (Google Cloud OAuth, YouTube `auth_cli`, provider dashboards) — use **browser + terminal first**; only ask the owner when blocked (wrong account, 2FA, payment). See `data/operating_rules_seed.md` → “Cloud agents — do it yourself first”.
- **Owner handoff:** if the owner must do something — drive the **browser to the exact screen** first, then they take over. No long manual doc dumps unless browser is unavailable.

## Cursor Cloud specific instructions

### North star (read first)

**Make a lot of money from 100% AI-automated YouTube Shorts channel(s)** — self-learning, self-improving, self-posting. No “human does 70%.”

**Work rule:** Only the **top 4** items in `docs/PRIORITIES.md` get built. Re-assess often.

**User:** Not a coder — explain in plain English, one step at a time.

**Long jobs (Replicate I2V, regen, QC):** always run in the **background** and do other work in parallel (docs, tests, commits, prompt fixes). Never sit idle waiting on shell — poll every 1–2 min.

**Video generation (owner rule):** `AI_VIDEO_GENERATION_ENABLED=false` by default — **no new Replicate I2V/FLUX** unless owner asks. Keep improving code, overlays, captions, upload meta, tests. **Render-only OK:** `python3 -m shorts_bot.production.render_pack_cli --draft-id N` (runs pack health first). **Pre-flight:** `python3 -m shorts_bot.production.pack_health_cli --draft-id N`.

### Project overview

**Shorts Bot** — Jenny Hoyos strategist CLI for **Peripheral** horror Shorts (merch tagline: *don't blink*). Knowledge base: **Codex** (`course/files/` 01–09, research, brand, learned rules). See `docs/CODEX.md`. **Paid stack:** **Gemini** (scripts + transcript + vision QC) + **Resemble** (cold narrator) + **Replicate I2V** (`VISUAL_STYLE=ai_video`). Keys via `bash scripts/install.sh`. Horror research: `data/research/HORROR_PSYCHOLOGY_DEEP_RESEARCH.md`. Applied learnings: `data/research/APPLIED_RESEARCH_ROUND_2.md`.

**Channel brand:** **Peripheral** (display name). Merch tagline: *don't blink* under line-eye logo. Spec: `channel/brand/identity.md`.

**Visual grammar (default):** fullscreen **CCTV** for security-cam drafts — **no phone screens**. Time via **alarm clock** or REC OSD (`screen_text_phone_enabled=false`).

**Channel mission:** terrifying ~30s micro-stories with **jumpscare at the end** — completion + binge, not cosy self-help. **Universe:** all Shorts live in **The Gap** (`channel/brand/world.md`, `shorts_bot/production/world.py`) — same alone-at-night apartment, lag between reality and recordings, 3:12 AM glitch hour. Launch QC playbook: `data/LAUNCH_QUALITY.md` (script bar, vision min 7.5, jumpscare sting on render). Horror VO: `tts_horror_delivery=true` — per-sentence dread/lunge prosody (Resemble SSML or edge-tts chunked).

**Live:** Video #1 mirror blink — https://youtube.com/shorts/-21Yc_xTcMY

**QA previews (YPP-safe):** Compare renders **locally** (`final_short_vN.mp4`). Do **not** upload `(build vN …)` iterations to YouTube under `YPP_SAFE_MODE` — batch QA uploads are **banned** (Jul 2025 inauthentic-content policy). One public/unlisted upload per draft max; 1 Short / 24h.

```bash
# Local render only — no YouTube upload for iteration builds
python3 -m shorts_bot.production.render_jumpscare_cli --draft-id 3 --render
# Single owner-approved upload (no build suffix, no --allow-duplicate-draft):
python3 -m shorts_bot.production.upload_unlisted_cli --draft-id 3 --no-render
```

See `docs/YPP_ANTI_SHADOWBAN.md` and `shorts_bot/compliance/ypp_bans.py`.

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

**Chief Manager (AlphaBeta001):** `python3 -m shorts_bot.agents.cli` — you talk to **AlphaBeta001** only (not the channel name); research underlings work behind the scenes (`MANAGER_WORK_PRIORITY=research` by default). Say `take 1h to research horror hooks` or `plan this week's hooks`. Web: `POST /api/manager/run`. See `docs/AGENT_MANAGER.md`. Discord optional. Override: `MANAGER_DISPLAY_NAME` in `.env`.

**Slack ↔ Cursor (long sessions away from IDE):** Official path is `@cursor` in Slack → Cloud Agent → replies in thread. Setup: `docs/SLACK_CURSOR_SETUP.md`. Slack MCP (`needsAuth` until owner links in Cursor Desktop) lets agents post/read Slack during grinds. Suggested channel: `#dont-blink-ops`, default repo `proof-codex-ai`.

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

**Automation (default on):** Background analytics sync, auto-Yes on safe improvements, scheduled `!daily`, **uploads go public** (`YOUTUBE_UPLOAD_VISIBILITY=public` — owner approved, no pre-review), **Gemini vision QC** + ffmpeg QC before upload, **YouTube API upload** (no Studio Playwright).

**Browser:** Playwright Chromium + `data/browser_profile/`. Discord/chat: `browse <url>`, `browser open vidiq`. Agent tools: `browse_web`, `open_browser`. `python3 -m shorts_bot.browser.cli status`. See `docs/BROWSER.md`.

### Codex (knowledge base)

**Codex** is the knowledge base name — Jenny strategist files in `course/files/` (01–09). Router picks files per user message. Offline: `course <question>` and `free tools` commands. See `docs/CODEX.md`.

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

### Production pipeline (target)

Fully automated: topic → script → render → QC → upload → publish → analytics → self-improve → repeat daily.

**Top 4 build order:** `docs/PRIORITIES.md` (video factory → upload API → daily runner → remove human gates).

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
