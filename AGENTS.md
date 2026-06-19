# AGENTS.md

## Owner (read first)

- **Not a developer** — explain in plain English; give exact steps ("open http://localhost:8080 and type `daily`"), not code tours.
- **North star:** autonomous money-making channel. **Current focus:** **100% automation** + **better videos** (hooks, sync, vision QC, analytics learning). Top 4 only in `data/PRIORITIES.md`.
- **Deprioritize** refactors, docs-for-docs-sake, and features that do not advance autopilot or revenue.
- **Top 4 only:** see `data/PRIORITIES.md` — work only on those four until reassessed; update the file when priorities shift.
- **Do it yourself:** external setup (Google Cloud OAuth, YouTube `auth_cli`, provider dashboards) — use **browser + terminal first**; only ask the owner when blocked (wrong account, 2FA, payment). See `data/operating_rules_seed.md` → “Cloud agents — do it yourself first”.
- **Owner handoff:** if the owner must do something — drive the **browser to the exact screen** first, then they take over. No long manual doc dumps unless browser is unavailable.

## Cursor Cloud specific instructions

### North star (read first)

**Make a lot of money from 100% AI-automated YouTube Shorts** — same channel, **AI/tech rebrand**, InVideo twin production, self-learning from analytics. No “human does 70%.”

**Work rule:** Only the **top 4** items in `docs/PRIORITIES.md` get built. Re-assess often.

**User:** Not a coder — explain in plain English, one step at a time.

**Video generation:** Homemade render (Recraft, Blender, ffmpeg) is **retired**. Target: **InVideo AI twin** after owner validates manually. See `data/research/CHANNEL_NICHE_STRATEGY.md`.

### Project overview

**Shorts Bot** — autonomous CLI for **AI/tech Shorts** on the existing YouTube channel. Knowledge base: **Codex** (`course/files/` 01–09 — hooks/retention still useful; horror rules deprecated). **Paid stack (target):** **Gemini** (scripts + QC) + **InVideo** (twin + stock + captions) + **YouTube upload API**. Keys via `bash scripts/install.sh`.

**Channel direction:** AI / Tech → sub-niche TBD → sub-sub-niche TBD. Strategy: `data/research/CHANNEL_NICHE_STRATEGY.md`. Brand stub: `channel/brand/identity.md`.

**Codex search (agents only — NOT for the owner):**

```bash
python3 -m shorts_bot.codex search "hook retention short form"
python3 -m shorts_bot.codex read data/research/CHANNEL_NICHE_STRATEGY.md
```

**Peripheral horror:** retired — archived under `archive/peripheral/`. Do not produce new horror content unless owner explicitly reverses.

**Formats:** Shorts now via InVideo; long-form later via winner compilation when new niche has 3+ hits.

**Channel mission:** ~30s AI/tech Shorts with **one clear takeaway** — verdict, myth bust, or workflow. InVideo twin presenter. See `data/research/CHANNEL_NICHE_STRATEGY.md`.

**QA previews (YPP-safe):** One public upload per draft max; 1 Short / 24h. Compare renders locally before canonical upload.

See `docs/YPP_ANTI_SHADOWBAN.md` and `shorts_bot/compliance/ypp_bans.py`.

### Slack (remote ops)

Owner OAuth required — agent cannot complete alone.

```bash
bash scripts/slack-setup.sh                    # print checklist
python3 -m shorts_bot.integrations test        # after SLACK_WEBHOOK_URL set
curl -s http://localhost:8080/api/slack/status
```

Docs: `docs/SLACK_CURSOR_SETUP.md`, `docs/SLACK_AUTOMATIONS.md`, `data/SLACK_SETUP_CHECKLIST.md`.

### Services

Install: `bash scripts/install.sh`

**Cursor Cloud Agent secrets:** add keys in Cursor → your cloud agent → Secrets (same names as below). Run `bash scripts/install.sh` on the VM to sync into `.env`. See secret checklist in `docs/CURSOR_SECRETS.md`.

Web UI (recommended):

```bash
python3 -m shorts_bot.web
# http://127.0.0.1:8080 (binds localhost by default)
```

Set `WEB_API_TOKEN` in `.env` to require Bearer token on mutating `/api/*` routes (UI auto-injects when served from `/`).

### Agent clock

Check the time before scheduling posts, daily autopilot, or time-sensitive replies:

```bash
python3 -m src.clock              # human-readable UTC + owner local (America/Los_Angeles)
python3 -m src.clock --json       # machine-readable
python3 -m src.clock --write      # refresh data/CLOCK.json snapshot
bash scripts/clock.sh --json
```

Override timezones: `OWNER_TIMEZONE=America/Chicago OPS_TIMEZONE=UTC python3 -m src.clock`

CLI:

```bash
python3 -m shorts_bot
```

Set `GEMINI_API_KEY` (free, preferred) or `OPENAI_API_KEY` for full conversational mode. Keys sync via `scripts/sync_secrets.py` on start. See `docs/CHAT_TONIGHT.md`. Without either, offline command mode still works (`help`, `draft`, `pending`, etc.).

**Chief Manager (AlphaBeta001):** `python3 -m shorts_bot.agents.cli` — you talk to **AlphaBeta001** only (not the channel name); research underlings work behind the scenes (`MANAGER_WORK_PRIORITY=research` by default). Say `take 1h to research horror hooks` or `plan this week's hooks`. Web: `POST /api/manager/run`. Remote: Slack `@cursor`. See `docs/AGENT_MANAGER.md`. Override: `MANAGER_DISPLAY_NAME` in `.env`.

**Slack ↔ Cursor (remote ops):** `@cursor agent …` in Slack starts Cloud Agents. **Option A (no bot token):** Gmail → `SLACK_CHANNEL_EMAIL` posts alerts to `#peripheral-ops` (`docs/FOR_OWNER_SLACK_EMAIL.md`). Or webhook `SLACK_WEBHOOK_URL` / bot token. Setup: `bash scripts/slack-setup.sh`, `docs/FOR_OWNER_SLACK.md`. Status: `GET /api/slack/status`, `python3 -m shorts_bot.integrations test`.

**Slack autonomy bus:** AlphaBeta001 posts `[autonomy] <command>` in `#peripheral-ops`; Socket Mode listener (with web UI running) executes via `BotOperations.chat` and replies in-thread — self-talk for 24/7 ops without IDE. Secrets: `SLACK_BOT_TOKEN`, `SLACK_CHANNEL_ID`, `SLACK_APP_TOKEN`. API: `POST /api/slack/autonomy`. CLI: `python3 -m shorts_bot.integrations autonomy status`. See `docs/SLACK_AUTONOMY.md`.

### Lint / test

No linter configured. Smoke checks:

```bash
pip install -r requirements.txt
python3 -m compileall -q shorts_bot src
python3 -m src.clock --json
python3 -m pytest tests/ -q
```

### Data

SQLite at `data/shorts_bot.db` (gitignored). Stores drafts, approvals, rejections, chat history.

**Agent memory (persistent):** operating rules / preferences / facts in `agent_memories` table; exported to `data/MEMORY.md`. Seeded from `data/operating_rules_seed.md` on first run. Injected into strategist + draft prompts; restored chat context on agent startup (`memory_chat_context_limit`, default 24). Commands: `remember <text>`, `memory`, `forget <id>` in web chat. CLI: `python3 -m shorts_bot.memory.memory_cli list`. See `docs/AGENT_MEMORY.md`.

**Deep research:** `research <topic>` / `deep research <topic>` — web browse, Google Trends, YouTube competitors, browser fallback. vidIQ off by default. See `docs/DEEP_RESEARCH.md`, `docs/BROWSER.md`.

**Self-learning:** Draft reject → immediate `avoid:*` rules; sync → reward proposals (max 3) + **reflective self-training** (episodes, rule confidence, promote to agent memory); safe improvements auto-approved. See `docs/SELF_LEARNING.md`, `docs/AUTONOMOUS_SELF_TRAINING_RESEARCH.md`. Config: `SELF_TRAINING_ENABLED=true`.

**Automation (default on):** Background analytics sync, auto-Yes on safe improvements, scheduled daily Short when `auto_daily_enabled=true`, **uploads go public** (`YOUTUBE_UPLOAD_VISIBILITY=public` — owner approved, no pre-review), **Gemini vision QC** + ffmpeg QC before upload, **YouTube API upload** (no Studio Playwright).

**Browser:** Playwright Chromium + `data/browser_profile/`. Web chat: `browse <url>`, `browser open vidiq`. Agent tools: `browse_web`, `open_browser`. `python3 -m shorts_bot.browser.cli status`. See `docs/BROWSER.md`.

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

### Dev queue

Web **Dev queue** panel or `dev: title | description` in chat — safe tasks auto-approve to `data/DEV_QUEUE.md`; login/payment tasks need approval in UI. Approved items also append to `data/LEARNED.md`.

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
