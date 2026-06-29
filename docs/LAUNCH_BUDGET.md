# Launch budget — 2+ month runway

**Owner numbers (Jun 2026):** ~**$2,283** cash · affiliate account ~**$630** · want **≥2 months** before broke.

**Owner priority (updated):** **FastMoss from day 1** — replaces EchoTik and Kalodata. **8–10 GOOD affiliate videos** as soon as launch — not a slow ramp.

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
| **FastMoss Basic** | **~$59/mo** | **Launch day** — required, not optional (replaces EchoTik + Kalodata) |
| Kling credits (day 1) | **~$5–15** | 8–10 clips + regens @ ~$0.21/5s (`KLING_MODE=std`) |
| Zernio | $0–150/mo | Confirm your plan — likely already live |
| Images (Higgsfield / ChatGPT) | ~$2–5 day 1 | Per product stills |

**Same-day stack (~$694–704 upfront + your Zernio plan):** account + FastMoss month 1 + first day Kling/images.

**Not required for affiliate day 1:** bubble phones 1–4 · full phone worker automation.

**Required for affiliate cart at launch:** **`phone_5`** (affiliate) — Zernio inbox draft + product link on device.

---

## Phase 1 — hardware (hub phones)

| Item | Qty | **Budget pick** |
|------|-----|-----------------|
| Used Android phones | **5** | **$250** ($50 each) |
| Powered USB hub + cables | 1 | **$30** |
| 5 prepaid SIMs (1st month) | 5 | **~$60** |
| Hub PC (old HP laptop) | 1 | **$0** |
| **Hardware total** | | **~$340** |

**5 phones:** 4 bubble (Mackenzie finish) + **1 affiliate** (`phone_5` — orange shopping cart / product link). Zernio can't attach Shop products via API.

---

## Monthly burn — full stack from affiliate launch

**No stagger.** FastMoss + full ~$385 stack turns on when affiliate posts start.

| Item | $/mo | Notes |
|------|------|-------|
| **FastMoss Basic** | **~$59** | Product research — **required at launch** (UI day 1; API scout when wired) |
| Zernio + misc SaaS | ~$100–200 | Confirm your Zernio tier |
| Kling (8–10 **good** /day) | ~$65–85 | ~240–300 published + ~20% QC regens |
| Images | ~$30–50 | Module 4 stills |
| 5 SIM lines | ~$60 | Bubble ×4 + affiliate `phone_5` |
| **Full affiliate month** | **~$384–444** | **~$420/mo** plan number |

FastMoss covers Kalodata-equivalent checks (ads, trend, filters) in one subscription — **no EchoTik, no separate Kalodata paywall**.

---

## Does 2 months still work?

### Plan A — affiliate first, phones within ~2 weeks *(fastest)*

| | Amount |
|--|--------|
| Working cash | $2,253 |
| Affiliate account | −$630 |
| Month 1 full stack (no SIMs yet) | −$384 |
| Bubble hardware (phones + hub + SIMs) | −$340 |
| Month 2 full stack (+ SIMs) | −$444 |
| **Buffer after 2 months** | **~$525** |

**Verdict: yes** — 2+ months, affiliate can post **today** after account + FastMoss subscribed.

### Plan B — buy everything upfront, full stack both months

| | Amount |
|--|--------|
| Working cash | $2,253 |
| Account + hardware (Phase 1) | −$910 |
| **Left for operations** | **$1,343** |
| Month 1 full stack | −$444 |
| Month 2 full stack | −$444 |
| **Buffer after 2 months** | **~$455** |

**Verdict: yes** — tighter buffer, but meets 2-month goal if you stay on budget hardware.

### Plan C — worst case (avoid)

High-end phones ($280) + hub ($40) + full stack day 1 + heavy Kling regens → buffer under **~$200**. Don’t.

**Rule of thumb:** keep **≥$200** emergency float. Both Plan A and B satisfy that.

---

## Launch day sequence (affiliate — 8–10 GOOD posts)

1. **Affiliate account purchased** → log in once in **Zernio** → paste ID into `affiliate_main` in `accounts.json`  
2. **FastMoss subscribed** → pick 8–10 in app (or `scout_cli ping` when API wired)  
3. **Products locked** → names in `products.json` (FastMoss UI picks or future API scout)  
4. **Parallel clip factory** — image → Kling 5s → pan loop + caption → **Module 1 QC** (zero violations)  
5. **Post 8–10 that pass QC** via Zernio — reject/regen failures, don’t upload bad clips  
6. **Bubble hardware** — buy/wire in parallel when cash allows; does not gate step 5  

**Day-1 Kling math:** 10 target posts + ~2 regens ≈ 12 clips × $0.21 ≈ **~$2.50–3** Kling only. “Good” costs time, not huge extra dollars — unless QC keeps failing (fix prompts, don’t brute-force regens).

---

## Recommended buy order (speed + runway)

1. **Haircut** — done.  
2. **Affiliate account (~$630)** — do this first.  
3. **FastMoss Basic (~$59)** — same day as first product picks / posts.  
4. **Zernio** — connect purchased account; enable `affiliate_main`.  
5. **Launch day** — scout → 8–10 QC-pass clips → post.  
6. **Bubble hardware (~$280)** — buy when ready; affiliate already running.  
7. **Wipe HP laptop** — when phones arrive.  

**Do not buy:** new mini PC · EchoTik · Kalodata subscription (FastMoss replaces both).

---

## When you’d go broke (watch these)

| Trigger | Rough hit |
|---------|-----------|
| Full ~$444/mo × 2 with upfront hardware | Buffer ~$455 — OK |
| Kling regen spiral (50+ extra clips/mo) | +$10–20/mo — fix QC/prompts, don’t pay your way out |
| Re-buy affiliate account | +$630 |
| 5th phone + SIM | +$60–85 upfront + ~$12/mo |

---

## Quick reference

| Question | Answer |
|----------|--------|
| FastMoss on day 1? | **Yes — required** (~$59/mo Basic) |
| EchoTik / Kalodata? | **No** — retired; FastMoss only |
| Posts on launch day? | **8–10 GOOD** (QC pass), not 1 test clip |
| Need phones first? | **No** — affiliate is cloud + Zernio |
| 2 months runway? | **Yes** (~$455–525 buffer on plan A/B) |
| 5th phone + SIM | **Yes — affiliate cart** (`phone_5`) |

Update when Zernio bill, FastMoss tier, or cash changes.
