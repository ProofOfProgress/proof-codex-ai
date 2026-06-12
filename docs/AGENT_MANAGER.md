# AlphaBeta001 — Chief Manager + specialist workers

**Don't Blink** uses **AlphaBeta001** as the Chief Manager (the agent you talk to). AlphaBeta001 is not the YouTube channel — the channel is Don't Blink. The manager delegates to small **Gemini specialists** behind the scenes. Discord is optional — use **CLI** or **web UI**.

## Who talks to whom

**You only talk to AlphaBeta001 (Chief Manager).** Underlings have no chat interface.

| Layer | Role | What it does |
|-------|------|----------------|
| **You** | Owner | One message in, one manager reply out |
| **AlphaBeta001** | Chief Manager / your interface | Plans, delegates, synthesizes |
| **Research Lead** | Mini-manager | Queues research underlings |
| **Deep Research Worker** | Underling | `deep_research_topic` → `data/research/*.json` |
| **Competitor Analyst** | Underling | Gap vs existing Shorts |
| **Hook Analyst** | Underling | Rank hooks + title formulas |
| **Trends Scout** | Underling | Google Trends + RPM notes |
| **Research Scout** | Underling | Fast hook/beat brief |
| **Niche Strategist** | Underling | Scores cosy/RPM topics |
| Script Writer | Underling | Drafts **only when you explicitly ask** |
| Quality Reviewer | Underling | Review (balanced/production mode) |

Internal audit log (not a chat UI): `data/underlings/work.log`

All use `GEMINI_API_KEY` via `shorts_bot/llm/provider.py`.

## Codex (internal — you don't use it)

**AlphaBeta001** reads Codex automatically on craft/strategy questions (hooks, suspense, retention, etc.) — BM25 search over ~609 chunks injected before the reply (`shorts_bot/codex/context.py`).

You just ask AlphaBeta001 normally. There is no `!codex` command or web button for you.

## Current priority: RESEARCH

Default `MANAGER_WORK_PRIORITY=research`:

- Underlings focus on **deep research stacks**, not drafts
- Say `draft` / `make video` if you want scripts created
- Plain messages like `plan cosy topics` auto-route to manager with a **3 min research burst** (`MANAGER_DEFAULT_RESEARCH_SECONDS=180`)

## Work duration — “take an hour to respond”

Tell the manager how long to **work before replying**. It fills that budget with real tasks (research, scoring, drafts), then answers with a summary.

### Phrases that work

```
take an hour to plan this week's cosy shorts
[30m] score topics for RPM
don't respond for 45 minutes — research attachment hooks
spend 2h on this: draft and review 3 topics
respond in 90 minutes
manager: take 20m to research sunday couch dread
```

| Syntax | Meaning |
|--------|---------|
| `take 1h` / `take an hour` | 3600s work budget |
| `[30m]` prefix | 30 minute budget |
| `don't respond for X` | Wait/work X before answer |
| `manager:` prefix | Always use Chief Manager (even without duration) |

Limits (`.env` / `config.py`):

- Floor: **30s** (`MANAGER_WORK_FLOOR_SECONDS`)
- Cap: **2 hours** (`MANAGER_MAX_WORK_SECONDS`)

## How to run

### Dedicated manager CLI (recommended)

```bash
python3 -m shorts_bot.agents.cli
```

One-shot:

```bash
python3 -m shorts_bot.agents.cli "take an hour to score cosy topics and draft the best one"
python3 -m shorts_bot.agents.cli --work 30m "plan this week"
```

### Strategist CLI (also routes duration messages)

```bash
python3 -m shorts_bot.bot.cli
```

### Web UI

- `POST /api/chat` — auto-detects duration; long jobs go async
- `POST /api/manager/run` — explicit manager endpoint
- `GET /api/manager/jobs/{id}` — poll async jobs
- `GET /api/manager/jobs` — recent jobs

Async kicks in when work budget ≥ **120s** (`MANAGER_ASYNC_THRESHOLD_SECONDS`).

## What happens during a 1-hour session (research priority)

Typical order (until budget runs out):

1. **Research Lead** — research queue plan
2. **Niche Strategist** — score 5 cosy topics (light)
3. **Full stack per topic** (×2–3):
   - Research Scout brief
   - Deep Research Worker (web + competitors + cache)
   - Competitor Analyst
   - Hook Analyst
   - Trends Scout
4. More **deep-only** passes on rotation topics if time remains
5. Drafts **only** if you said `draft` / `make video`

Footer lists underling tasks + `data/research/` file paths. Say `pending` only if drafts were created.

## Config

```env
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-2.5-flash-lite
MANAGER_ENABLED=true
MANAGER_WORK_FLOOR_SECONDS=30
MANAGER_MAX_WORK_SECONDS=7200
MANAGER_ASYNC_THRESHOLD_SECONDS=120
MANAGER_WORK_PRIORITY=research
MANAGER_AUTO_DELEGATE=true
MANAGER_DEFAULT_RESEARCH_SECONDS=180
MANAGER_RESEARCH_FORCE_REFRESH=false
```

## Files

| Path | Role |
|------|------|
| `shorts_bot/agents/manager.py` | Chief Manager (your only interface) |
| `shorts_bot/agents/underlings/team.py` | UnderlingTeam dispatch |
| `shorts_bot/agents/underlings/research_lead.py` | Research Lead |
| `shorts_bot/agents/underlings/research_workers.py` | Research underlings |
| `shorts_bot/agents/work_loop.py` | Research-priority scheduler |
| `shorts_bot/agents/priority.py` | research / balanced / production |
| `shorts_bot/agents/duration.py` | Parse “take 1h” |
| `shorts_bot/agents/runner.py` | Gemini calls |
| `shorts_bot/agents/job_store.py` | Async job persistence |
