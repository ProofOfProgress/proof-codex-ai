# Daily posting without messaging Cursor

**Cursor automations are not reliable for TikTok posting.** They often show “success” when the automation rule was saved — not when your clip posted.

**What actually works:** an **always-on machine** runs a **cron job** every 30 minutes. No chat message needed.

---

## Why Cursor automations fail here

| Cursor automation | What you need |
|-------------------|---------------|
| Spins up an agent when triggered | A process that runs **whether or not** you open Cursor |
| Cloud VM may not stay running 24/7 | **HP hub laptop** (or VPS) stays on |
| “Success” = rule created | **Success** = Zernio accepted the upload |

---

## Architecture

```
Cloud agent (you or me in chat)
  → makes clips, QC, enqueue to data/tiktok_shop/queue.json

HP hub laptop (always on) — cron every 30 min
  → bash scripts/affiliate_cron.sh
  → posts ONE queued clip if spacing + quota allow
  → Zernio → TikTok affiliate account
```

**Affiliate does not need you to upload manually.** The hub (or any always-on PC) is the **clock**, not Cursor.

---

## One-time setup on the HP hub

After WSL + `bash scripts/install.sh` + `.env` / secrets:

```bash
cd ~/proof-codex-ai
bash scripts/install_hub_cron.sh
```

Or paste manually:

```bash
crontab -e
```

Add:

```
*/30 * * * * cd /home/YOU/proof-codex-ai && bash scripts/affiliate_cron.sh >> data/tiktok_shop/scheduler.log 2>&1
```

---

## Check it’s working (no Cursor chat)

```bash
python3 -m shorts_bot.tiktok_shop.factory_cli scheduler status
tail -20 data/tiktok_shop/scheduler.log
python3 -m shorts_bot.tiktok_shop status
```

Manual one-shot (same as cron):

```bash
bash scripts/affiliate_cron.sh
```

Dry run (no upload):

```bash
python3 -m shorts_bot.tiktok_shop.factory_cli scheduler tick --account affiliate_main
```

---

## Before cron can post

1. **Purchased affiliate account** connected in Zernio  
2. `affiliate_main.enabled` = `true` + `zernio_account_id` in `accounts.json`  
3. `ZERNIO_API_TOKEN` on the **hub machine** (in `.env` or environment)  
4. **Queue has clips** — cloud agent (or you) runs `enqueue` after QC pass  
5. Clips + `queue.json` live on the **same machine as cron** (sync repo + `data/` folder)

---

## Spacing rules (Module 1)

- **≥30 minutes** between posts on the same account (cron every 30 min = safe)  
- **8–10 posts/day** cap per account  
- Cron **skips** when: queue empty, daily cap hit, or too soon since last post  

---

## Bubble wrap

Bubble still needs phones for Mackenzie sound. Affiliate MP4 posts **do not** — cron + Zernio only.
