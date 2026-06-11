# Priority list — reassess often

**Rule:** Agents and bots may **only** work on the **top 4** items below until the owner changes this file or approves a reorder. Everything else is backlog.

**Goal right now:** **100% automation** + **better videos** (using the most important levers to improve them).

**North star (unchanged):** Self-learning, fully autonomous channel that makes a lot of money — automation and quality are how we get there.

**Last assessed:** 2026-06-11 (Video #1 live — see `data/PRIORITY_14_NOW.md` for full top-14 list)

---

## Top 4 (only these until reassessed)

| # | Priority | What it means | Most important levers | Status |
|---|----------|---------------|----------------------|--------|
| **1** | **100% automation** | Bot runs the full day without you: idea → script → voice → video → quality check → upload → stats sync | `auto_daily`, pipeline resume, auto analytics sync, auto-approve safe learning rules, comment triage | **Mostly built** — must run 24/7 where bot lives; remove any step that still needs a human click |
| **2** | **Better hooks & scripts** | People swipe away in 1 second if the opening is weak | Jenny hook rules, analytics punish/reward, draft rejections → avoid rules, topic/hook cooldowns | **Built** — needs steady uploads + sync so data flows |
| **3** | **Better visuals & sync** | Video must *look* right and match the voice beat-by-beat | **Don't Blink horror I2V** (terrifying motion clips, end jumpscare beat), Gemini transcript timing, ffmpeg captions, **vision QC** | **Live** — no stick figures; ai_video only |
| **4** | **Learn from every video** | Each Short teaches the next one | YouTube retention/views → reflect loop; vision QC fails → avoid rules; approved patterns → repeat rules | **In progress** — close the loop so quality gains compound without you |

---

## What “better videos” means (in order of impact)

1. **Hook** — first line earns the next 3 seconds  
2. **Retention pacing** — 6–8 beats, ~2–3s cuts, concrete protocol payoff  
3. **Visual sync** — horror motion clips + final scare beat synced to VO  
4. **Captions** — readable, safe zone, mute-friendly  
5. **QC before upload** — bot rejects blurry, frozen, or sloppy renders  
6. **Analytics feedback** — double down on what kept viewers watching  

---

## Backlog (not top 4 — do not distract)

- Slack / mobile Cursor setup (useful remote control, not the pipeline)
- Home PC My Machines, git/ZIP on Windows
- Cursor API key injection, Enterprise pools, TikTok
- CapCut operator, dev queue UI, refactors unless they block top 4

---

## How we reassess

Update this file when the owner shifts focus or a top-4 item is done. Tell the owner in **plain English**.
