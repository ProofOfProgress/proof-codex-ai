# Phone hub — mini computer + 5 Android phones

**Pre-launch buy (owner):** mini computer + **5 cheap Android phones** + **5 SIM cards** + purchased affiliate account.

```
You / Cloud agent  →  Mini computer  →  5 Android phones (USB hub)
                           │                    │
                     runs the bot          one TikTok each
                     controls phones 1-4   Mackenzie + publish (bubble)
                     phone 5             affiliate logged in (Zernio MP4 posts)
```

---

## Phone map

| Slot | TikTok | Track | Posts/day | Mini PC job |
|------|--------|-------|-----------|-------------|
| `phone_1` | gspgsgsorip1 | bubble **safe** | 3–4 | Inbox → Mackenzie → publish |
| `phone_2` | proofofprogresss | bubble **aggressive** | 8–10 | Same |
| `phone_3` | Ms. Byte | bubble **aggressive** | 8–10 | Same |
| `phone_4` | Isaac | bubble **safe** | 3–4 | Same |
| `phone_5` | **Purchased affiliate** | affiliate | 8–10 | Account lives here; **bot posts MP4 via Zernio** (no Mackenzie) |

Zernio IDs for bubble four: `accounts.json` · refresh: `python3 -m shorts_bot.zernio.auth_cli`

---

## Why 5 phones

- **4 bubble** — API can’t attach Mackenzie; mini PC must finish on the **correct** phone.  
- **1 affiliate** — dedicated device for the bought account (login, showcase, trust). Posting is automated via Zernio, not manual taps.

**One phone = one TikTok. Never switch accounts on one device.**

---

## Bubble flow (phones 1–4)

1. Bot creates 2 bubble images (`BUBBLE_WRAP.md`)  
2. Zernio → **inbox draft** to that account  
3. Mini PC → ADB on **`phone_N`** → TikTok → Mackenzie sound → publish  

## Affiliate flow (phone 5)

1. Bot: research → Kling → caption → QC  
2. Zernio posts MP4 to purchased account  
3. Phone 5 stays logged in; you don’t post by hand  

---

## What’s ready vs not built

| Ready | After hardware arrives |
|-------|------------------------|
| 4 bubble TikToks in Zernio | Mini PC + 5 phones + SIMs |
| Account → phone map in config | ADB + remote access |
| Affiliate account purchase | Connect in Zernio, enable `affiliate_main` |
| Docs + agent team | Carousel inbox + phone automation (build) |

Physical hub — **not** cloud phone farm.

**Mackenzie:** https://www.tiktok.com/music/original-sound-7418286946344340256

Full timeline: `docs/LAUNCH_CHECKLIST.md`
