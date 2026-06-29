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
| 4 bubble TikToks in Zernio | Phones plugged in + USB serials in `devices.json` |
| Account → phone map in config | Mackenzie UI automation (needs live phones) |
| **`shorts_bot/phone_hub/`** — ADB, job queue, worker dry-run | Full publish automation on device |
| Bubble → Zernio inbox draft + hub job queue | WSL usbipd attach per phone |
| Affiliate pipeline (cloud) | Purchased affiliate → Zernio → enable `affiliate_main` |
| Hub auto-connect (SSH) | `hub_adb_install.sh` on laptop (agent can run remotely) |

Physical hub — **not** cloud phone farm.

---

## Agent / hub commands (no phones needed yet)

Cloud agent (auto-connects to laptop):

```bash
bash scripts/hub_run.sh bash scripts/hub_adb_install.sh   # install adb once
bash scripts/hub_run.sh bash scripts/hub_adb_check.sh   # health check
python3 -m shorts_bot.phone_hub.cli status              # slot map + pending jobs
python3 -m shorts_bot.phone_hub.cli tick                # dry-run next hub job
```

Bubble post flow (cloud):

```bash
python3 -m shorts_bot.tiktok_shop.factory_cli bubble-slides --subject frog
python3 -m shorts_bot.tiktok_shop.factory_cli post-carousel \
  --slide1 ... --slide2 ... --account bubble_gspgsgsorip1 \
  --confirm --enqueue-hub
```

When phones arrive: fill `adb_serial` in `data/phone_hub/devices.json`, then `python3 -m shorts_bot.phone_hub.cli tick --confirm`.
