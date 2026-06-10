# Chief Manager + specialist workers

Soft Continuity uses a **Chief Manager** (what you talk to) that delegates to small **Gemini specialists** behind the scenes. Discord is optional — use **CLI** or **web UI**.

## Who talks to whom

| You talk to | It runs |
|-------------|---------|
| **Chief Manager** | Plans, delegates, synthesizes final reply |
| Niche Strategist | Scores cosy/RPM topics |
| Research Scout | Hooks, beats, competitor gaps (+ cached deep research) |
| Script Writer | 60s protocol scripts → pipeline drafts |
| Quality Reviewer | Rejects vague/office slop |
| Content Manager | Plans the work queue for your time budget |

All specialists use `GEMINI_API_KEY` via `shorts_bot/llm/provider.py`.

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

## What happens during a 1-hour session

Typical order (until budget runs out):

1. Content Manager — work plan
2. Niche Strategist — score 5 cosy topics
3. Research Scout — deep research on top pick
4. Script Writer — pipeline draft + quality review
5. More research on rotation topics if time remains

Footer lists tasks completed and `draft #` if created. Say `pending` to review.

## Config

```env
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-2.5-flash-lite
MANAGER_ENABLED=true
MANAGER_WORK_FLOOR_SECONDS=30
MANAGER_MAX_WORK_SECONDS=7200
MANAGER_ASYNC_THRESHOLD_SECONDS=120
```

## Files

| Path | Role |
|------|------|
| `shorts_bot/agents/manager.py` | Chief Manager |
| `shorts_bot/agents/work_loop.py` | Timed work budget |
| `shorts_bot/agents/duration.py` | Parse “take 1h” |
| `shorts_bot/agents/runner.py` | Gemini specialist calls |
| `shorts_bot/agents/tasks.py` | Research, draft, review units |
| `shorts_bot/agents/job_store.py` | Async job persistence |
