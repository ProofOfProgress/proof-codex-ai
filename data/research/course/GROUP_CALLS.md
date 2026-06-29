# Group calls — live course updates

**Momentum Academy** rules and prompt styles **change often**. Static module files are the baseline; **group calls are the live source of truth**.

## Owner workflow

After each group call, tell the agent what changed. Example:

> “Group call 6/12: stop saying ‘violently discounted’ — use ‘clearing extra stock’ instead. CTR target still 5%.”

The agent should:

1. Append a dated note to `data/research/course/GROUP_CALLS.md` (or update the relevant module section)
2. Update bot rules if needed (`captions.py`, `module1_qc.py`, prompt templates)
3. **Not** guess — only encode what the owner reports from the call

## What usually changes on calls

- On-screen **caption / prompt text** styles (Module 6)
- **Banned or risky words** (Module 7)
- Product research filters (Module 3)
- Violation / appeal tactics (Module 8)
- **Violation waves** — wait for coach playbook; owner logs in GROUP_CALLS

## Modules that explicitly say “join group calls”

- Module 6 — caption prompt copy  
- Module 7 — avoiding violations & misinformation wording  
- Module 8 — violation waves + appeal strategy updates

Module 1 visual/posting don’ts stay mandatory unless the owner says otherwise.

---

## 2026-06-28 — System dissection rule (owner)

When agents **diagnose or fix any problem** (grey borders, QC fail, still-image look, etc.), they must **dissect the whole pipeline** and fix **code + rules + tests + docs** — **not** just re-render one clip or patch one output.

Cursor rule: `.cursor/rules/system-dissection.mdc` · Example: borders → Gemini sample step + 9:16 gates + prep fix, not `--force` on one MP4.

---

## 2026-06-28 — Module 1 brand + phone screen rules (owner)

**Only the advertised product's brand** may appear in frame — no recognizable third-party logos (Apple, MacBook, Instagram, Nike, competitors, etc.).

**No phone screens** — home screen, app icons, notifications, lit mobile UI. Treat as banned **even if static** (not just "moving screens").

**No recognizable apps** in frame.

Enforced in: `module_01_read_before_anything.md`, `module1_qc.py`, Gemini sample prompts, Kling negatives, `product-video-prompt-builder`.

---

## 2026-06-28 — Operating strategy (owner)

**Parallel tracks:** 4 bubble-wrap growth accounts **and** affiliate revenue posting — not either/or.

**Bubble wrap cadence (4 accounts):**
- **2 safe** — 3–4 posts/day each  
- **2 aggressive** — 8–10 posts/day each  

**Affiliate go-live:** **FastMoss** for research + **8–10 GOOD posts** when account + Zernio are live. Full ~$450/mo stack on at first post.

**Pre-launch buy:** purchased **affiliate account (~$630)** first; bubble hardware (**4 phones + SIMs + laptop hub ~$280**) can follow in parallel — see `docs/LAUNCH_BUDGET.md`.

**Phone hub:** 4 phones on laptop — bubble Mackenzie finish. Affiliate = Zernio MP4 from cloud (no 5th phone). See `FOR_OWNER_PHONE_HUB.md` · `LAUNCH_CHECKLIST.md`

**Bubble cadence:** **Safe** — gspgsgsorip1, Isaac @ 3–4/day. **Aggressive** — proofofprogresss, Ms. Byte @ 8–10/day.

**Launch (Phase 2):** FastMoss + full stack + **8–10 affiliate posts launch day** — bubble ramp when hub wired.

---

## 2026-06-28 — Week 1 challenge (owner)

**Course reward:** **$1,000 commission** in **7 calendar days** → **$500 bonus**.

- **Clock starts:** **12:00 AM** first live post on chosen **Launch Date** (not dry runs).  
- **Clock:** **7 calendar days** — Launch Date midnight through **11:59 PM on day 7** (Launch Date + 6 days).  
- **Why midnight:** maximizes the full first day.  
- **Target pace:** ~**$143/day** average; course peers hit **$100 days in a week**.  
- **Execution:** `docs/LAUNCH_TODO.md` — LAUNCH is Section I; posts #1–10 spaced ≥30m from midnight.  
- **Daily:** 8–10 GOOD posts, track commission, double down on winners, drop losers.

---

## 2026-06-28 — FastMoss replaces EchoTik (owner)

**Course creator:** FastMoss is as good as Kalodata.

**One research tool:** **FastMoss only** — **not** EchoTik, **not** Kalodata.

- **Subscribe:** [fastmoss.com](https://www.fastmoss.com/) (~$59/mo Basic — verify on site)
- **Launch path A:** pick 8–10 products in FastMoss app → tell agent names
- **Launch path B:** FastMoss API in bot when scout ships — `docs/FASTMOSS_SCOUT_PLAN.md`
- **Do not pay EchoTik**
