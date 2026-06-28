# Phone hub — mini computer + Android phones

**Owner plan (strategy — hardware not purchased yet):**

```
You / Cloud agent  →  Mini computer  →  4 Android phones (USB hub)
                           │                    │
                     runs the bot          one TikTok each
                     controls phones       Mackenzie sound + publish
```

From the loan plan: **small computer (~$300) runs posting overnight** + **each account gets its own phone and data line**.

---

## Why this exists

- **Bubble wrap** needs **Mackenzie sound** — TikTok API cannot attach it.
- You don’t trust manual uploads on one phone (fair).
- **One phone = one TikTok** — mini computer picks the right device so you never post to the wrong account.

**Affiliate does not use the phone hub** — bot posts finished MP4 via Zernio (no sound step).

---

## The 4 bubble TikToks (Zernio — all active)

| phone_hub_slot | TikTok @ | Zernio ID | Tier (you assign) |
|----------------|----------|-----------|-------------------|
| `phone_1` | gspgsgsorip1 | `6a3e03579d9472faaeecbab6` | safe or aggressive |
| `phone_2` | proofofprogresss | `6a3f14df9d9472faaef98701` | safe or aggressive |
| `phone_3` | Ms. Byte *(repurposed → bubble)* | `6a39dedb5f7d1751ab57366b` | safe or aggressive |
| `phone_4` | Isaac | `6a3e5a0b9d9472faaef19baa` | safe or aggressive |

Config: `data/tiktok_shop/accounts.json` · refresh: `python3 -m shorts_bot.zernio.auth_cli`

**Cadence:** 2 accounts @ **3–4/day** (safe) · 2 @ **8–10/day** (aggressive) — you’ll label which is which.

---

## End-to-end flow (when built)

### Bubble wrap (phone hub path)

1. **Cloud agent / bot** — create 2 bubble images (format in `BUBBLE_WRAP.md`)
2. **Zernio API** — send 2-photo **inbox draft** to the correct `zernio_account_id`
3. **Mini computer** — via ADB, open TikTok on **`phone_N`** only (mapped in `accounts.json`)
4. **Mini computer** — add Mackenzie sound → publish
5. You can **remote into the mini computer** to watch or override — you don’t touch each phone by hand unless something breaks

### Affiliate (no phone hub)

1. Product research → Kling → edit → Module 1 QC  
2. **Zernio** posts MP4 directly — done

---

## What’s prep vs what’s not built yet

| Ready now | When hub hardware exists |
|-----------|-------------------------|
| 4 TikToks in Zernio | Mini computer on your network |
| `accounts.json` slot map | 4 phones plugged in, ADB enabled |
| Bubble format docs | Automation: inbox → sound → publish per phone |
| Zernio video post (affiliate) | Photo carousel → inbox (bubble — building) |

**Not cloud phone farm** — physical phones on a USB hub, controlled by your mini PC.

---

## Mackenzie sound

https://www.tiktok.com/music/original-sound-7418286946344340256  

See `BUBBLE_WRAP.md` for slide format.

---

## Parallel tracks (full picture)

| Track | Accounts | Posts/day | How |
|-------|----------|-----------|-----|
| Bubble wrap | 4 above | 3–4 or 8–10 each | Mini PC + phone hub |
| Affiliate | TBD separate account | 8–10 | Full bot via Zernio |

Both run in parallel while bubble accounts grow toward 1k.
