# Launch budget — 2+ month runway

**Owner numbers (Jun 2026):** ~**$2,283** cash · affiliate account ~**$630** · want **≥2 months** before broke.

**Owner priority (updated):** **EchoTik from day 1** (Kalodata is expensive too). **8–10 GOOD affiliate videos** as soon as launch — not a slow ramp.

Strategy: `LAUNCH_CHECKLIST.md` · hardware: `FOR_OWNER_MINI_PC_INSTALL.md`

---

## Starting point

| | Low | High | Plan with |
|--|-----|------|-----------|
| Cash on hand | $2,283 | $2,283 | $2,283 |
| Haircut (one-time) | −$20 | −$40 | **−$30** |
| **Working cash** | **$2,243** | **$2,263** | **$2,253** |

---

## What “launch” means now

**Affiliate goes first.** Bubble phones do **not** block affiliate posting.

| Track | Needs hardware? | Day-1 target |
|-------|-----------------|--------------|
| **Affiliate** | No — cloud + Zernio only | **8–10 GOOD posts** (Module 1 QC pass) |
| **Bubble wrap** | Yes — 4 phones + laptop hub | Starts when hub wired (parallel, not first) |

**GOOD** = Module 1 QC pass, course caption/edit, no sale/price words — not “post whatever renders.” Budget **~20% extra Kling** for regens (failed QC or bad motion).

---

## Minimum to post affiliate today

Buy/pay these **before** the first affiliate post:

| Item | Cost | When |
|------|------|------|
| Purchased affiliate account | **~$630** | Now |
| **EchoTik paid** | **~$125/mo** | **Launch day** — required, not optional |
| Kling credits (day 1) | **~$5–15** | 8–10 clips + regens @ ~$0.21/5s (`KLING_MODE=std`) |
| Zernio | $0–150/mo | Confirm your plan — likely already live |
| Images (Higgsfield / ChatGPT) | ~$2–5 day 1 | Per product stills |

**Same-day stack (~$760–770 upfront + your Zernio plan):** account + EchoTik month 1 + first day Kling/images.

**Not required for affiliate day 1:** 4 phones · USB hub · SIMs · laptop hub · phone worker.

---

## Phase 1 — hardware (bubble track — can lag affiliate)

| Item | Qty | **Budget pick** |
|------|-----|-----------------|
| Used Android phones | **4** | **$200** ($50 each) |
| Powered USB hub + cables | 1 | **$30** |
| 4 prepaid SIMs (1st month) | 4 | **$50** |
| Hub PC (old HP laptop) | 1 | **$0** |
| **Hardware total** | | **$280** |

Skip 5th phone — affiliate posts via Zernio from cloud.

---

## Monthly burn — full stack from affiliate launch

**No stagger.** EchoTik + full ~$450 stack turns on when affiliate posts start.

| Item | $/mo | Notes |
|------|------|-------|
| **EchoTik paid** | **~$125** | Product scout — **required at launch** |
| Zernio + misc SaaS | ~$100–200 | Confirm your Zernio tier |
| Kling (8–10 **good** /day) | ~$65–85 | ~240–300 published + ~20% QC regens |
| Images | ~$30–50 | Module 4 stills |
| 4 SIM lines | ~$50 | Bubble only — $0 until phones live |
| **Full affiliate month** | **~$450–510** | **~$500/mo** plan number |

Kalodata: course login still useful for **spot-checks** (ad badge, trend) on EchoTik finalists — **not** the primary research tool (too expensive to rely on daily).

---

## Does 2 months still work?

### Plan A — affiliate first, phones within ~2 weeks *(fastest)*

| | Amount |
|--|--------|
| Working cash | $2,253 |
| Affiliate account | −$630 |
| Month 1 full stack (no SIMs yet) | −$450 |
| Bubble hardware (phones + hub + SIMs) | −$280 |
| Month 2 full stack (+ SIMs) | −$500 |
| **Buffer after 2 months** | **~$393** |

**Verdict: yes** — 2+ months, affiliate can post **today** after account + EchoTik paid.

### Plan B — buy everything upfront, full stack both months

| | Amount |
|--|--------|
| Working cash | $2,253 |
| Account + hardware (Phase 1) | −$910 |
| **Left for operations** | **$1,343** |
| Month 1 full stack | −$500 |
| Month 2 full stack | −$500 |
| **Buffer after 2 months** | **~$343** |

**Verdict: yes** — tighter buffer, but meets 2-month goal if you stay on budget hardware.

### Plan C — worst case (avoid)

High-end phones ($280) + hub ($40) + full stack day 1 + heavy Kling regens → buffer under **~$200**. Don’t.

**Rule of thumb:** keep **≥$200** emergency float. Both Plan A and B satisfy that.

---

## Launch day sequence (affiliate — 8–10 GOOD posts)

1. **Affiliate account purchased** → log in once in **Zernio** → paste ID into `affiliate_main` in `accounts.json`  
2. **EchoTik paid** → `python3 -m shorts_bot.tiktok_shop.scout_cli ping` green  
3. **Scout run** → top products in `products.json` (EchoTik presets; owner picks or approves batch)  
4. **Parallel clip factory** — image → Kling 5s → pan loop + caption → **Module 1 QC** (zero violations)  
5. **Post 8–10 that pass QC** via Zernio — reject/regen failures, don’t upload bad clips  
6. **Bubble hardware** — buy/wire in parallel when cash allows; does not gate step 5  

**Day-1 Kling math:** 10 target posts + ~2 regens ≈ 12 clips × $0.21 ≈ **~$2.50–3** Kling only. “Good” costs time, not huge extra dollars — unless QC keeps failing (fix prompts, don’t brute-force regens).

---

## Recommended buy order (speed + runway)

1. **Haircut** — done.  
2. **Affiliate account (~$630)** — do this first.  
3. **EchoTik paid (~$125)** — same day as first scout/post.  
4. **Zernio** — connect purchased account; enable `affiliate_main`.  
5. **Launch day** — scout → 8–10 QC-pass clips → post.  
6. **Bubble hardware (~$280)** — buy when ready; affiliate already running.  
7. **Wipe HP laptop** — when phones arrive.  

**Do not buy:** 5th phone · new mini PC · Kalodata subscription (EchoTik is the daily tool).

---

## When you’d go broke (watch these)

| Trigger | Rough hit |
|---------|-----------|
| Full $500/mo × 2 with upfront hardware | Buffer ~$343 — OK but tight |
| Kling regen spiral (50+ extra clips/mo) | +$10–20/mo — fix QC/prompts, don’t pay your way out |
| Re-buy affiliate account | +$630 |
| 5th phone + SIM | +$60–85 upfront + ~$12/mo |

---

## Quick reference

| Question | Answer |
|----------|--------|
| EchoTik on day 1? | **Yes — required** |
| Kalodata instead? | **No** — too expensive; EchoTik daily, Kalodata optional spot-check only |
| Posts on launch day? | **8–10 GOOD** (QC pass), not 1 test clip |
| Need phones first? | **No** — affiliate is cloud + Zernio |
| 2 months runway? | **Yes** (~$343–393 buffer on plan A/B) |
| 5th phone? | **No** |

Update when Zernio bill, EchoTik tier, or cash changes.
