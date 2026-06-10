# Priority list — reassess often

**Rule:** Agents and bots may **only** work on the **top 4** items below until the owner changes this file or approves a reorder. Everything else is backlog.

**North star:** Self-learning, fully autonomous YouTube channel that makes **a lot of money**.

**Last assessed:** 2026-06-09 (owner correction: channel has already posted — setup is not the bottleneck)

---

## Top 4 (only these until reassessed)

| # | Priority | Why it matters | Status |
|---|----------|----------------|--------|
| **1** | **Daily autopilot — 1 Short/day, no babysitting** | Money needs consistent posts; upload path already worked before | **Code ready** — Discord `auto_daily` + pipeline; must stay ON wherever bot runs (Discord/home/cloud) |
| **2** | **Self-learning loop closed** | Bot must get smarter from uploads + analytics + **vision QC** (not just views) | **In progress** — wiring vision QC → avoid rules + upload snapshots |
| **3** | **Analytics → next video** | Sync YouTube stats, auto-apply safe hook/retention wins, punish flops | **Mostly built** — needs steady uploads + sync running |
| **4** | **Shrink human steps toward zero** | Full autopilot = less unlisted hand-holding over time | **Owner choice** — `AUTO_PUBLISH_HOURS=0` keeps manual review; raise when trust is high |

---

## Backlog (not top 4 — do not distract)

- Home PC **My Machines** (`shorts-home`) — optional reliability, not required if uploads already work elsewhere
- `git` / ZIP download on Windows — only if moving bot to a new machine
- Cursor API key / cloud VM secret injection
- Enterprise self-hosted pools, TikTok, CapCut operator, dev queue polish
- Refactors and merge cleanup unless they block #1–4

---

## How we reassess

Update this file when a top-4 item completes, a blocker appears, or the owner redirects. Notify owner in **plain English**.
