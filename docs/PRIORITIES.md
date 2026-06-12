# Priorities — North Star

**North star:** Make a lot of money from **100% AI-automated** YouTube Shorts channel(s) — self-learning, self-improving, self-posting, self-operating. **No “human does 70%.”**

**Rule:** We only work on the **top 4** priorities. Everything else waits. Re-assess this list often (after every major ship or blocker).

---

## Honest status (today)

What the pasted chat *claimed* vs what this repo *actually has*:

| Area | Chat claimed | Repo reality |
|------|----------------|--------------|
| Script writing | Working | **Yes** — drafts + quality checks |
| Voice + video render | Working | **No** — no TTS, ffmpeg, or render pipeline in repo |
| Vision QC | Added | **No** — not in codebase |
| CapCut automation | Done | **No** — only a style guide markdown file |
| YouTube upload | Needs login once | **Partial** — OAuth + analytics sync; **no upload API** |
| Daily autopilot | Almost there | **No** — no scheduler / daily runner |
| Auto-publish | Unlisted review | **No** — human Yes/No on drafts + improvements everywhere |
| `login_status`, `CURSOR_SECRETS.md`, Gemini/Resemble | Documented | **Not in this repo** — may exist elsewhere or were planned |
| Cursor API / My Machines | Tested | **Useful later** — not required to post the first automated Short |
| Windows `shorts-home` worker | User stuck on ZIP download | **Still blocked** — project not fully on home PC yet |

**Bottom line:** You have a strong **brain** (ideas, scripts, learning rules). You do **not** yet have **hands** (make video → upload → post daily without you). That gap is why there’s no money yet.

---

## Priority list (ranked for money + full automation)

### Top 4 — only these get worked on

| # | Priority | Why it’s top 4 | Done when |
|---|----------|----------------|-----------|
| **1** | **Video factory** — script → voice → visuals → rendered `.mp4` | No video = no views = $0. Biggest hole. | Approved script automatically becomes a finished Short file on disk |
| **2** | **YouTube publish API** — upload + set visibility + metadata, no Studio clicks | Distribution. OAuth exists; upload code doesn’t. | One command uploads a rendered Short without human in YouTube Studio |
| **3** | **Daily autopilot runner** — unattended loop: pick topic → make → QC → upload → log | Consistency = algorithm + revenue. | Cron / scheduler runs 1+ Shorts/day with zero manual trigger |
| **4** | **Remove human gates** — replace Yes/No with automated rules | “70% human” today is draft approve, improvement approve, private→public, dev queue. | Bot auto-approves when quality + vision scores pass thresholds; auto-publishes per policy |

### Backlog — do not touch until top 4 ship

| # | Item | Why it waits |
|---|------|----------------|
| 5 | Closed-loop money optimization (auto-tune hooks/topics/times from analytics) | Needs videos live first |
| 6 | Multi-channel scaling (clone pipeline per niche) | Needs one channel printing first |
| 7 | My Machines / `shorts-home` worker | Helps OAuth + heavy render on your PC; not a substitute for #1–#3 in code |
| 8 | Cursor API orchestration (agents spawning agents) | Meta-dev; doesn’t post Shorts |
| 9 | Web UI polish | Nice; doesn’t post Shorts |
| 10 | Dev queue / self-coding automation | Engineering convenience; not revenue |
| 11 | More documentation | Only if it unblocks #1–#4 |

### Stop doing (wastes north-star time)

- Pretending CapCut/upload/daily are “done” in docs when code isn’t there
- Cursor API testing unless it runs the daily pipeline
- UI glow-ups, extra chat commands, dev-queue features
- Asking you to do coding steps beyond one-time Google Allow + keeping a worker window open

---

## What “100% automated” means (target)

```
EVERY DAY (no human):
  research topic → write script → make video → QC → upload → public/unlisted per rule
  → sync analytics → adjust next video → repeat

HUMAN (one-time or never):
  ✗ approve every draft
  ✗ flip private → public
  ✗ tap Yes/No on improvements
  ✓ optional: one-time Google “Allow” for OAuth token
  ✓ optional: spend limit / kill switch you set once
```

---

## Your immediate unblock (you, not code)

You’re stuck on **Windows setup** — project folder exists at `C:\Users\p1nea\proof-codex-ai` but worker isn’t running yet.

**Next paste in PowerShell (one line at a time):**

```powershell
cd C:\Users\p1nea\proof-codex-ai
dir
```

You must see `shorts_bot` in the list. Then:

```powershell
agent login
agent worker start --name "shorts-home"
```

Reply **“worker is running”** when the last line stays open without a red error. That unblocks Google login on *your* machine — still needed until upload API runs from a server with a saved token.

---

## How we re-assess

After each ship, ask:

1. Did this post a Short or directly enable posting? If no → deprioritize.
2. Did this remove a human step? If no → lower priority.
3. Are we still only working on items 1–4? If not → stop and refocus.

---

## For agents (AGENTS.md points here)

- User is **not a coder** — plain English, one step at a time.
- **Money from fully automated channels** beats everything else.
- **Top 4 only.** No side quests.
