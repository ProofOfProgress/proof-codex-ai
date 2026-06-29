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
3. Hub → ADB on **`phone_5`** → open draft → **Add Link → Products** → pick showcase item → publish  

Until UI automation ships, step 3 can be a quick manual tap on `phone_5` — bot still does steps 1–2.

---

## What's built vs not

| Done | Not yet |
|------|---------|
| 4 bubble + affiliate slot in config | Phones plugged in + USB serials in `devices.json` |
| Affiliate → Zernio **inbox draft** + hub job queue | `add_product_link` UI automation on device |
| Bubble → inbox draft + hub queue | Mackenzie UI automation (needs live phones) |
| **`shorts_bot/phone_hub/`** — ADB, job queue, worker | Full publish automation on device |
| Hub auto-connect (SSH) | usbipd attach per phone |

Physical hub — **not** cloud phone farm.

---

## Agent / hub commands

Cloud agent (auto-connects to laptop):

```bash
bash scripts/hub_run.sh bash scripts/hub_adb_install.sh
bash scripts/hub_run.sh bash scripts/hub_adb_check.sh
python3 -m shorts_bot.phone_hub.cli status
python3 -m shorts_bot.phone_hub.cli tick                # dry-run next hub job
```

Affiliate post (cloud — enqueues phone_5 when `affiliate_main` has slot + Zernio id):

```bash
python3 -m shorts_bot.tiktok_shop.factory_cli post --account affiliate_main --confirm
python3 -m shorts_bot.phone_hub.cli tick --confirm      # on hub when phone_5 wired
```

When phones arrive: fill `adb_serial` in `data/phone_hub/devices.json`.
