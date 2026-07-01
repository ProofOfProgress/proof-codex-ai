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

**Pre-launch buy:** purchased **affiliate account (~$630)** first; hub hardware (**5 phones + SIMs + laptop ~$340**) — see `docs/LAUNCH_BUDGET.md`.

**Phone hub:** 5 phones — 4 bubble (Mackenzie) + **1 affiliate (`phone_5`)** for shopping cart / product link (Zernio can't attach via API). See `FOR_OWNER_PHONE_HUB.md`

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

---

## 2026-07-01 — CEO mindset + North Star (owner, voice)

**North Star:** **50 phones operational** in bedroom hub **within 6 months** — reinvest profits into hardware + automation.

**CEO mindset:** Attack every blocker like an RPG boss — system fix, retry, grow. CEO runs daily ops; owner stays principal (legal, money, logins). **Last word** before irreversible actions (drop accounts, cut owner access, major unbudgeted spend). Consider owner offers seriously.

**Phase order (owner):** **Bubble wrap live first** (4 auto accounts) → affiliate clips ~4 days out.

**Encoded:** `data/CEO_MINDSET.md` · `.cursor/rules/ceo-mindset.mdc` · `data/PRIORITIES.md`

---

## 2026-06-29 — Owner launch status

- **Purchased affiliate account:** bought, logged in, **5-day warmup** in progress.
- **FastMoss:** payment blocked — owner contacted support; scout/API blocked until resolved.
- **Kling:** billing works.
- **Launch Date:** TBD · **Timezone:** PST (midnight first post = 12:00 AM PST on Launch Date).
- **Bubble + affiliate:** both tracks active — affiliate does not wait for phones.

### Owner overrides (hard rules)

- **Zernio — defer:** Do **not** connect purchased affiliate account to Zernio until **closer to launch** (owner will say when). Until then: prep clips, QC, queue locally — no `affiliate_main` in Zernio dashboard.
- **Phone number — never on bot account:** The purchased affiliate account’s **phone number must never** be tied to the bot, Cursor secrets, Zernio hookup, or automation. Login path for posting = **email only** when Zernio is wired later. Do not ask owner to add phone to secrets or link phone to `affiliate_main`.

---

## 2026-06-29 — Account seller intel (GMV / bought accounts)

**Source:** Official account seller plug (owner relay) — high-GMV bought-account operator.

**Q:** Most important thing for making money with affiliate videos (excluding consistency)?

**A:** **Finding products before they break out** is “1000% of everything” — how people get 20M-view videos. Already-top products are good; **future top products are literal gold**.

**Bot / research implication:**

- Module 3 priority = **early breakout**, not only current chart toppers.
- In FastMoss: favor **rising** GMV/creator velocity, new releases, ad spend starting, trend **up** before mainstream saturation.
- Scout presets and agent research should weight **pre-breakout signals** over “safe” established winners alone.

---

## 2026-06-29 — Full agent ownership (owner)

**Product research is entirely the agent’s job** — not a one-step owner task. Owner does **not** pick products in FastMoss or paste names for launch.

**Business handoff:** Affiliate ops → **100% agent-run soon**. Owner stays for **improvements**, decisions, and account/billing access when required — not daily research or clip ops.

**Agent owns:** Module 3 research (FastMoss scout / product-researcher), `products.json`, pre-breakout lens, clip pipeline, QC, queue — end to end.

**Owner does not own:** Product picks · “send me 2–3 product names” · FastMoss UI browsing for launch list.

---

## 2026-06-29 — Account seller Discord wins (owner relay)

**Source:** Discord bundled with bought account (account seller’s community + second course). **Customer wins** channel — recent posts (many June 2025/2026).

**Pattern in wins (commission unless noted as GMV):**

- New / bought accounts hitting **$1k–$10k+ commission** in first weeks; **Gold/Silver** tiers first month
- **$1k+ in a single day** commission — multiple reports
- **$4k–$7k+ in 7 days**; **$8k–$51k in 30 days** commission range across posts
- **$42k in 19 days** (June 1–20) cited; **~$95k GMV in 30 days** (GMV ≠ commission — still validates demand)
- Some still “figuring out convert” at **$6.5k** — room to optimize
- **Livestreams** mentioned in wins — **we are NOT doing livestreams** (short affiliate video lane only)

**Owner read:** Proven concept on **bought warmed accounts + volume + product timing**. Aligns with pre-breakout research intel and 8–10 posts/day plan.

**Scale vision (owner):** “30 automated accounts × 10/day” — aspirational **later**. **Current plan:** 1 affiliate revenue account + 4 bubble growth accounts. Do not scope-creep bot to 30 accounts without owner explicit go + budget + ban-risk review.

**Agent implication:** Speed to launch + pre-breakout picks + GOOD post volume matter — winners in that Discord are the comp, not a guarantee.

---

## 2026-06-29 — Course creator convo (owner relay)

**Context:** Owner talking to **Momentum Academy course creator**. Creator shipped free bubble-wrap video automation ( ~10 full video gens/day on course site). Creator’s “hush hush” = full stack: research → image → video → edit → post — same north star as this repo.

**Creator offer:** “Build it and let me see. If you cook, I’ll pay you.”

**Owner decisions (hard for agents):**

- **Demo rule:** If/when owner demos to creator — show **finished video output only** (generation result). **Zero** behind-the-scenes: no repo, no agents, no Zernio, no pipeline docs, no architecture, no “peek through keyhole.”
- **IP / distribution:** Owner **keeping full automation private for now** — not selling/licensing to creator or course yet. Concern: mass distribution → market flood (many users × many accounts × automation).
- **Competition note:** Creator’s free tool does **not** upload to TikTok — owner assesses this repo ahead on posting + full affiliate lane.
- **TOS priority:** Owner betting **one purchased affiliate account** — Module 1 QC + deep TOS compliance is **existential**, not nice-to-have. “Good” beats “functional” (creator agreed). Agent must not shortcut QC or violate Module 1/7 for speed.

**Not doing:** YouTube AI content / “sell out” lane — owner locked on TikTok Shop until exit.

---

## 2026-06-29 — Official coach: still-frame violation fix (content review — law)

**Source:** Registered Momentum Academy coach reviewed owner **Insulated Tumbler** clip in content review chat.

**Verdict:** Product good · video quality good · **needs more movement** to avoid **still-frame violation**.

**Coach guidance (encode everywhere — prompts, Module 6 post, QC):**

- TikTok is **very strict** — still-frame strikes happen even when the clip has “decent” or “plenty of” movement.
- **~25% more side-to-side** camera travel — lateral parallax must be **noticeable**, not subtle orbit-only.
- Add **micro-shake** (handheld) **and/or** background objects that shift vs the product (proves camera is moving).
- Product can stay fixed; **camera** must show clear multi-axis + lateral motion.
- **Trial and error** on scripts — consistency + scale is the game.

**Pipeline changes (repo):**

- `video_variants.make_pan_loop_clip` — post-process lateral boost + micro-shake before forward/reverse loop.
- `module1_qc.py` — inter-frame motion score + Gemini still-frame lens.
- `product-video-prompt-builder` — emphasize lateral sweep + background parallax in every Kling prompt.

**Regenerate** existing clips (e.g. tumbler) with new prompt + re-run loop — do not repost old MP4.

---

## 2026-06-29 — Daily pre-launch CEO mission (owner)

**Goal:** Before launch, **one automated kickoff per day** on hub laptop — scout/plan products, paste **CEO prompt** into Cursor, **click Run** (desktop helper). Cloud agent then generates that day's affiliate clips (research → Kling → QC → queue locally, **no Zernio**).

**Owner calibrates:** focus + submit click coords in Cursor UI. Guide: `docs/FOR_OWNER_DAILY_PRELAUNCH.md`.
