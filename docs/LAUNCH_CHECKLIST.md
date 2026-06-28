# Launch checklist

**Affiliate first:** 8–10 **GOOD** posts (Module 1 QC pass) as soon as account + EchoTik are live. Bubble hardware runs in parallel — it does **not** block affiliate.

**Budget:** `docs/LAUNCH_BUDGET.md` — $2,283 cash, ~$630 account, EchoTik day 1, **≥2 months runway**.

**Step-by-step to-do (in order):** `docs/LAUNCH_TODO.md` — **$1k in 7 calendar days → $500 course bonus.**

---

## Affiliate launch *(do this first — can be today)*

### Before first affiliate post

| Step | Item |
|------|------|
| 1 | **Purchased affiliate TikTok account** (~$630) |
| 2 | **EchoTik paid** (~$125/mo) — scout is required; Kalodata is not the daily tool |
| 3 | Connect account in **Zernio** → `affiliate_main` in `accounts.json` |
| 4 | Kling + images funded (`KLING_MODE=std`, ~$0.21/5s clip) |
| 5 | `python3 -m shorts_bot.tiktok_shop status` — EchoTik, Kling, Zernio green |

### Launch day — 8–10 GOOD videos

| Step | Action |
|------|--------|
| 1 | `scout_cli run` → products in `products.json` |
| 2 | Batch clips: image → Kling 5s → pan loop + caption |
| 3 | **Module 1 QC on every clip** — zero violations or regen |
| 4 | Post **8–10 QC-pass** MP4s via Zernio (reject bad renders) |
| 5 | Daily ops: repeat scout + 8–10/day cap |

**GOOD** = course edit + caption + Module 1 pass — not raw Kling output.

**Launch timing:** pick a **Launch Date**; first post at **12:00 AM** that day (maximize 7 days for $1k bonus). See `LAUNCH_TODO.md` Section H–I.

**Not required for affiliate launch:** phones · SIMs · laptop hub · phone worker · bubble posts.

---

## Phase 1 — Bubble hardware *(parallel — not a gate)*

| Item | Qty | Budget tip |
|------|-----|------------|
| **Mini computer** | 1 | **Old HP laptop** — wipe + Ubuntu. $0. |
| **Cheap Android phones** | **4** | Used $40–70 each. **No 5th phone.** |
| **SIM cards / data lines** | **4** | ~$10–15/mo each. One per bubble phone. |
| **Powered USB hub + cables** | 1 | ~$25–40 |

**Rough one-time:** ~$280 (phones + hub + SIM activations) · **$0 PC**

Install: `docs/FOR_OWNER_MINI_PC_INSTALL.md`

---

## Phase 2 — Full stack billing

Turn on when **affiliate posts start** (not when phones arrive):

| Item | ~$/mo |
|------|-------|
| **EchoTik paid** | ~$125 |
| Zernio + Kling + images + misc | ~$325 |
| 4 SIMs (when bubble live) | ~$50 |
| **Total** | **~$450–500/mo** |

---

## Account plan

### Bubble — 4 existing TikToks (Zernio hooked)

| Phone | Cadence | Account | Posts/day |
|-------|---------|---------|-----------|
| phone_1 | **Safe** | gspgsgsorip1 | 3–4 |
| phone_4 | **Safe** | Isaac | 3–4 |
| phone_2 | **Aggressive** | proofofprogresss | 8–10 |
| phone_3 | **Aggressive** | Ms. Byte | 8–10 |

Hub PC finishes **Mackenzie sound + publish** on the mapped phone.

### Affiliate — purchased account

| Account | Posts/day | How |
|---------|-----------|-----|
| **Purchased account** (Zernio) | **8–10 on launch day** | Cloud pipeline → QC → Zernio MP4 |

---

## Bubble wire checklist (when hardware arrives)

1. Laptop on network (Tailscale for remote access)  
2. **4 phones:** ADB on, one bubble TikTok each  
3. **Build:** carousel → Zernio inbox → hub → Mackenzie → publish  
4. Ramp safe accounts first, then aggressive  

---

## Product research

**EchoTik** = daily scout (paid tier at launch).  
**Kalodata** = optional spot-check on EchoTik finalists (ad badge, trend) — not a launch substitute.

Config: `data/tiktok_shop/accounts.json` · Hub: `FOR_OWNER_PHONE_HUB.md` · Budget: `LAUNCH_BUDGET.md`
