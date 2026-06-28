# Launch checklist — when you buy, we go

**Launch is not a soft “start posting.”** Launch **engages when you buy everything** — hardware, purchased affiliate account, and paid software stack. Until then: strategy + code prep only.

---

## Account plan (owner 6/2026)

### Bubble wrap — 4 existing TikToks (Zernio hooked)

| Cadence | Account | Posts/day |
|---------|---------|-----------|
| **Safe** | gspgsgsorip1 | 3–4 |
| **Safe** | Isaac | 3–4 |
| **Aggressive** *(more trusted)* | proofofprogresss | 8–10 |
| **Aggressive** *(more trusted)* | Ms. Byte | 8–10 |

Each maps to **one phone** on the mini PC hub (`accounts.json` → `phone_hub_slot`).

### Affiliate revenue — **purchased account**

- **Separate** from the 4 bubble accounts  
- Connect in Zernio when you have it  
- **8–10 affiliate MP4 posts/day** — full bot pipeline, no phone hub  

---

## What to buy (launch package)

| Item | Purpose | Track |
|------|---------|-------|
| **Mini computer** | Runs bot + controls phones overnight | Bubble |
| **4 Android phones** + USB hub + **4 data lines** | One TikTok per phone | Bubble |
| **Purchased affiliate TikTok account** | Revenue posts | Affiliate |
| **EchoTik API paid tier** (~$125/mo) | Automated product research | Affiliate |
| **Fixed stack** (~$325/mo total w/ above) | Zernio, etc. | Both |
| **Kling / Higgsfield credits** | Clips | Affiliate |
| *(Optional)* Printify API | Your own listings | Affiliate |

**~$450/mo** all-in at operating level (your number) + one-time hardware + account purchase.

---

## After purchase — what we build / turn on

### Bubble (4 accounts)

1. Mini PC on network (you can remote in; agent can reach it later)  
2. Phones plugged in, ADB on, one TikTok per device  
3. **Build:** 2-image carousel → Zernio inbox  
4. **Build:** mini PC opens TikTok on correct phone → Mackenzie sound → publish  
5. Ramp safe accounts, then aggressive  

### Affiliate (purchased account)

1. Connect purchased account in **Zernio** → enable `affiliate_main` in `accounts.json`  
2. **EchoTik paid** → scout runs daily (product picks)  
3. **One live clip** end-to-end: product → Kling → caption → QC → post  
4. Daily agent ops: research → clip → queue → 8–10/day  

Both tracks run **in parallel** once each path works.

---

## Kalodata “hardcore lurkers / 100 gap” — plain English

**You can ignore this until affiliate scout is running.**

That line was about **affiliate product research only** — not bubble wrap.

In the course, Kalodata has **saved filter presets** with names like:
- **hardcore lurkers**
- **100 gap**
- 200 method, middle core

Those presets find products worth promoting. When we automate research with **EchoTik** instead of you clicking Kalodata, we need to copy the **same filter rules** into code. “Screenshots” just meant: if you ever open those presets in Kalodata, we could match the exact numbers.

**At launch:** you can still pick products in **Kalodata manually** (course login) while EchoTik scout catches up. Not a blocker for buying hardware or posting bubble content.

---

## Launch order (simple)

```
1. BUY — mini PC, phones, data, affiliate account, EchoTik + monthly stack
2. WIRE — Zernio IDs, phone hub, remote access to mini PC
3. PROVE — one bubble post + one affiliate post end-to-end
4. RAMP — safe bubble → aggressive bubble + affiliate daily volume
```

---

Config: `data/tiktok_shop/accounts.json` · Phone hub: `FOR_OWNER_PHONE_HUB.md` · Strategy: `GROUP_CALLS.md`
