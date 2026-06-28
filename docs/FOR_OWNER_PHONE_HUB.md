# Phone hub — laptop + 4 Android phones

**Pre-launch buy (owner):** wipe **old laptop** as hub PC + **4 cheap Android phones** + **4 SIM cards** + purchased affiliate account.

**Budget math:** `docs/LAUNCH_BUDGET.md` — skip 5th phone; affiliate posts via Zernio from cloud.

```
You / Cloud agent  →  Laptop hub  →  4 Android phones (USB hub)
                           │                    │
                     runs the bot          one bubble TikTok each
                     controls phones 1-4   Mackenzie + publish (bubble)

Affiliate (purchased account)  →  Zernio MP4 posts from cloud — no hub phone required
```

---

## Phone map

| Slot | TikTok | Track | Posts/day | Hub job |
|------|--------|-------|-----------|---------|
| `phone_1` | gspgsgsorip1 | bubble **safe** | 3–4 | Inbox → Mackenzie → publish |
| `phone_2` | proofofprogresss | bubble **aggressive** | 8–10 | Same |
| `phone_3` | Ms. Byte | bubble **aggressive** | 8–10 | Same |
| `phone_4` | Isaac | bubble **safe** | 3–4 | Same |
| *(none)* | **Purchased affiliate** | affiliate | 8–10 | **Zernio MP4** from cloud agent |

Zernio IDs for bubble four: `accounts.json` · refresh: `python3 -m shorts_bot.zernio.auth_cli`

---

## Why 4 phones (not 5)

- **4 bubble** — API can’t attach Mackenzie; hub PC must finish on the **correct** phone.  
- **Affiliate** — bot posts finished MP4 via **Zernio**; connect the bought account once in Zernio dashboard. Optional login on your personal phone for showcase health.

**One phone = one TikTok. Never switch accounts on one device.**

---

## Bubble flow (phones 1–4)

1. Bot builds 2-image carousel  
2. Zernio → **inbox draft** to that account  
3. Hub PC → ADB on **`phone_N`** → TikTok → Mackenzie sound → publish  

## Affiliate flow (no hub phone)

1. Bot: research → Kling → caption → QC  
2. Zernio posts MP4 to purchased account  

---

## What’s built vs not

| Done | Not yet |
|------|---------|
| 4 bubble TikToks in Zernio | Laptop wiped + `install.sh` + ADB |
| Account → phone map in config | Phone hub worker (Mackenzie automation) |
| Affiliate pipeline (cloud) | Carousel inbox → hub worker |
| Docs + agent team | Purchased affiliate → Zernio → enable `affiliate_main` |

Physical hub — **not** cloud phone farm.
