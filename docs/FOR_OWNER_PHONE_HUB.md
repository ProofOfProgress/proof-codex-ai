# Phone hub — laptop + 5 Android phones

**Pre-launch buy (owner):** hub laptop + **5 Android phones** + **5 SIMs** + purchased affiliate account.

**Budget math:** `docs/LAUNCH_BUDGET.md` — 4 bubble + **1 affiliate phone** (~$330 hardware).

```
You / Cloud agent  →  Laptop hub  →  5 Android phones (USB / ADB)
                    │              →  Windows desktop (keyboard/mouse helper)
                           │
                     runs the bot          bubble: inbox → Mackenzie → publish
                     controls PC UI         affiliate: inbox → product link → publish

Affiliate (purchased account)  →  Zernio MP4 **inbox draft** → **phone_5** adds orange cart → publish
```

**Two control lanes:** **`FOR_OWNER_PHONE_HUB.md`** (this file) + **`FOR_OWNER_DESKTOP_HELPER.md`** (PC keyboard/mouse).

**One phone first?** See **`FOR_OWNER_ONE_PHONE_SETUP.md`** — wire `phone_1`, prove bubble flow, copy to other slots later.

---

## Phone map

| Slot | TikTok | Track | Posts/day | Hub job |
|------|--------|-------|-----------|---------|
| `phone_1` | gspgsgsorip1 | bubble **safe** | 3–4 | Inbox → Mackenzie → publish |
| `phone_2` | proofofprogresss | bubble **aggressive** | 8–10 | Same |
| `phone_3` | Ms. Byte | bubble **aggressive** | 8–10 | Same |
| `phone_4` | Isaac | bubble **safe** | 3–4 | Same |
| `phone_5` | **Purchased affiliate** | affiliate | 8–10 | Inbox → **Add Link → Products** → publish |

Zernio IDs: `accounts.json` · refresh: `python3 -m shorts_bot.zernio.auth_cli`

---

## Why 5 phones

- **4 bubble** — API can't attach Mackenzie; each account finishes on its own phone.
- **1 affiliate** — API / Zernio **can't attach the shopping cart**; `phone_5` adds the product link in TikTok before publish.

**One phone = one TikTok. Never switch accounts on one device.**

**Phone number rule:** The purchased affiliate account's SIM can live on `phone_5` for TikTok login — but that number **never** goes into Cursor secrets, Zernio API config, or bot automation. Zernio connect = **email + password only**.

---

## Bubble flow (phones 1–4)

1. Bot builds 2-image carousel  
2. Zernio → **inbox draft** to that account  
3. Hub → ADB on **`phone_N`** → TikTok → Mackenzie sound → publish  

## Affiliate flow (phone 5)

1. Bot: research → Kling → caption → Module 1 QC  
2. Zernio → **inbox draft** (MP4) to purchased account  
3. Hub → ADB on **`phone_5`** → automated **Add Link → Products** → publish (phone worker).

---

## What's built vs not

| Done | Not yet |
|------|---------|
| 5-phone slot map + Zernio inbox drafts | USB serials in `devices.json` |
| **Automated** Mackenzie + product link + publish (ADB worker) | One-time `ui_coords.json` calibration on real phones |
| Hub worker daemon (`phone_hub.cli serve`) | Live soak test when hardware arrives |
| Hub SSH + desktop helper | usbipd attach (if WSL doesn't see devices) |

Physical hub — **not** cloud phone farm.

---

## Agent / hub commands

Cloud agent (auto-connects to laptop):

```bash
bash scripts/hub_run.sh bash scripts/hub_adb_install.sh
bash scripts/hub_run.sh bash scripts/hub_adb_check.sh
python3 -m shorts_bot.phone_hub.cli status
python3 -m shorts_bot.phone_hub.cli tick                # dry-run next hub job
bash scripts/hub_run.sh bash scripts/hub_phone_screen.sh phone_1   # screenshot + text
```

**Phone screen for agent:** `hub_phone_screen.sh` saves `data/phone_hub/screenshots/last_phone_1.png` + JSON transcript on the hub. Cloud agent can read it over SSH. Optional Gemini describe when `GEMINI_API_KEY` is on the laptop.

Affiliate post (cloud — enqueues phone_5 when `affiliate_main` has slot + Zernio id):

```bash
python3 -m shorts_bot.tiktok_shop.factory_cli post --account affiliate_main --confirm
python3 -m shorts_bot.phone_hub.cli tick --confirm      # on hub when phone_5 wired
```

When phones arrive: fill `adb_serial` in `data/phone_hub/devices.json`, copy `ui_coords.json.example` → `ui_coords.json`, then:

```bash
python3 -m shorts_bot.phone_hub.cli serve          # hub daemon — drains inbox jobs
# or one-shot:
python3 -m shorts_bot.phone_hub.cli tick --confirm --max 10
```
