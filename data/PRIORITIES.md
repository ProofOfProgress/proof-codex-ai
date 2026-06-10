# Priority list — reassess often

**Rule:** Agents and bots may **only** work on the **top 4** items below until the owner changes this file or approves a reorder. Everything else is backlog.

**North star:** Self-learning, fully autonomous YouTube channel that makes **a lot of money**.

**Last assessed:** 2026-06-09

---

## Top 4 (only these until reassessed)

| # | Priority | Why it matters | Status | Owner action |
|---|----------|----------------|--------|--------------|
| **1** | **Home PC online (`shorts-home`)** | Bot needs *your* computer for Google login, uploads, and renders | **In progress** — project folder found; worker not started yet | Run `agent login` then `agent worker start --name "shorts-home"` and leave window open |
| **2** | **YouTube connected (one time)** | No uploads or analytics learning without this | **Blocked** on #1 | Click **Allow** in browser when we run YouTube sign-in |
| **3** | **Daily autopilot: 1 Short/day end-to-end** | Revenue needs consistent posts: script → video → QC → unlisted upload | **Built in code**; not running on your machine yet | After #1–2: bot runs daily; you optionally skim unlisted videos |
| **4** | **Self-learning loop closed** | Bot must get smarter from views, retention, rejections, vision QC | **Partial** — analytics + reflect exist; vision QC not fully wired to learning | Automatic once #3 runs for ~1–2 weeks |

---

## Not top 4 (do not spend time here unless #1–4 are done)

- Cursor API key injection / cloud VM secret quirks
- Enterprise self-hosted **pools** (you have **My Machines** — enough)
- TikTok automation
- New features: CapCut operator, extra Discord polish, dev queue UI
- Refactors, doc-only work, merge-conflict cleanup (unless it blocks #1–4)
- Making uploads **public** automatically (keep unlisted review until you trust the bot)

---

## How we reassess

Update this file when:

- A top-4 item is **done** (move next backlog item up)
- Something **blocks** money or autopilot (bump it into top 4, drop something else)
- Owner says priorities changed

After each reassessment, change **Last assessed** date and notify the owner in plain English.
