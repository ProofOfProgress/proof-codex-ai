# Launch checklist

Two phases — **pre-launch buy** (hardware + account) then **launch** (paid stack + posting).

**Budget:** `docs/LAUNCH_BUDGET.md` — $2,283 cash, ~$630 account, **≥2 months runway** (stagger software; 4 phones not 5).

---

## Phase 1 — Pre-launch buy *(buy before first post)*

| Item | Qty | Budget tip |
|------|-----|------------|
| **Purchased affiliate TikTok account** | 1 | — |
| **Mini computer** | 1 | **Use old HP laptop** — wipe + Ubuntu (see below). Saves ~$100–300 vs buying new. |
| **Cheap Android phones** | **4** | Used/refurb $40–70 each. **Skip 5th phone** — affiliate posts via Zernio. |
| **SIM cards / data lines** | **4** | ~$10–15/mo each prepaid. One per bubble phone. |
| **Powered USB hub + cables** | 1 set | ~$25–40. Don’t skip — unpowered hubs drop phones. |

**Rough one-time (budget path):** ~$200–350 phones + ~$25 hub + **$0 PC if laptop works**  
**Rough monthly:** ~$40–60 data (4 lines) — software stack (~$450/mo) starts at **launch**, not pre-launch.

### Old laptop as the hub PC

If you have an HP (or any laptop) with unknown password: **yes, wipe it** — F11 HP recovery, or Ubuntu USB install (`Erase disk`). Then install the bot per `docs/FOR_OWNER_MINI_PC_INSTALL.md`. Linux is ideal for ADB + 4 phones.

**Not in pre-launch buy:** EchoTik paid tier, full ~$450/mo software stack — those turn on at **launch**.

After Phase 1 arrives: wire phones, log each TikTok on its **own** phone only, connect affiliate account in Zernio, mini PC on network. **Install:** `docs/FOR_OWNER_MINI_PC_INSTALL.md`

---

## Phase 2 — Launch *(paid stack + go live)*

| Item | Purpose |
|------|---------|
| **EchoTik paid** (~$125/mo) | Automated product scout |
| **Rest of ~$450/mo stack** | Zernio, Kling credits, etc. |
| **Build + prove** | One bubble post + one affiliate post end-to-end |
| **Ramp** | Safe bubble → aggressive bubble + affiliate 8–10/day |

**Launch engaged** when Phase 1 is wired **and** Phase 2 software is paid **and** first posts go out.

Until Phase 1: strategy + code prep only.

---

## Account plan

### Bubble — 4 existing TikToks (Zernio hooked)

| Phone | Cadence | Account | Posts/day |
|-------|---------|---------|-----------|
| phone_1 | **Safe** | gspgsgsorip1 | 3–4 |
| phone_4 | **Safe** | Isaac | 3–4 |
| phone_2 | **Aggressive** *(trusted)* | proofofprogresss | 8–10 |
| phone_3 | **Aggressive** *(trusted)* | Ms. Byte | 8–10 |

Mini PC finishes **Mackenzie sound + publish** on the mapped phone.

### Affiliate — purchased account

| Account | Posts/day | How |
|---------|-----------|-----|
| **Purchased account** (Zernio) | 8–10 | Bot posts **MP4 via Zernio** from cloud — **no 5th phone** on budget path |

Affiliate does **not** need Mackenzie or a hub phone. Connect the bought account once in Zernio; optional login on your personal phone for showcase health.

---

## After Phase 1 — wire checklist

1. Mini PC on network (remote access for you + agent later)  
2. **4 phones:** ADB on, **one bubble TikTok each**, never switch accounts on a device  
3. Purchased affiliate → Zernio dashboard → `affiliate_main` in `accounts.json`  
4. **Build:** bubble carousel → inbox → mini PC → sound → publish (phones 1–4)  
5. **Build:** affiliate clip pipeline → Zernio post (no hub phone)

---

## After Phase 2 — first posts

1. One **bubble** carousel live (safe account first)  
2. One **affiliate** clip live (Module 1 QC pass)  
3. Ramp cadence per table above  

Both tracks in **parallel**.

---

## Kalodata filters — ignore until affiliate scout runs

Course product filters (hardcore lurkers, etc.) = **affiliate research only**. Manual Kalodata is fine at launch. Not a pre-launch buy item.

---

Config: `data/tiktok_shop/accounts.json` · Hub: `FOR_OWNER_PHONE_HUB.md` · Strategy: `GROUP_CALLS.md`
