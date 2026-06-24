# TikTok Shop factory — 3 accounts, 10 videos/day each

**Target:** 3 Shop affiliate accounts × **10 faceless product videos per day** = **30 total/day**.

No character. No VO. Short sale-style captions. Variants (not identical dupes).

---

## What you need first (one-time)

1. **3 TikTok accounts** with **Shop Affiliate** turned on  
2. Connect each to **Zernio** (easiest for multi-account) OR TikTok API tokens  
3. **EchoTik API** — bot scouts products daily (see `docs/FOR_OWNER_ECHOTIK_SETUP.md`)  
4. Render clips (Kling 5s pan-zoom → bot loops to ~10s)

---

## Configure accounts

Copy the example and fill in Zernio account IDs:

```bash
cp data/tiktok_shop/accounts.example.json data/tiktok_shop/accounts.json
```

Edit `data/tiktok_shop/accounts.json`:

| Field | What to put |
|-------|-------------|
| `id` | `shop_1`, `shop_2`, `shop_3` |
| `daily_limit` | `10` (leave as-is) |
| `zernio_account_id` | From zernio.com dashboard for each TikTok |
| `post_via` | `zernio` (recommended) or `tiktok_api` |

Find Zernio IDs:

```bash
python3 -m shorts_bot.zernio.auth_cli status
```

---

## Daily commands

**Check progress (how many posted today per account):**

```bash
python3 -m shorts_bot.tiktok_shop.factory_cli status
```

**Kalodata filter cheat sheet (manual UI reference):**

```bash
python3 -m shorts_bot.tiktok_shop.factory_cli rules
```

**Scout products via EchoTik (automated — use this daily):**

```bash
python3 -m shorts_bot.tiktok_shop.scout_cli status
python3 -m shorts_bot.tiktok_shop.scout_cli run --preset middle_core --limit 10
python3 -m shorts_bot.tiktok_shop.scout_cli list
```

Setup: `docs/FOR_OWNER_ECHOTIK_SETUP.md`

**Make ~10s clip from 5s Kling export:**

```bash
python3 -m shorts_bot.tiktok_shop.factory_cli loop-clip \
  --in data/tiktok_shop/clips/product_a_raw.mp4 \
  --out data/tiktok_shop/clips/product_a_loop.mp4
```

**Caption ideas (no % off):**

```bash
python3 -m shorts_bot.tiktok_shop.factory_cli captions --product "Car phone mount"
```

**Add to queue:**

```bash
python3 -m shorts_bot.tiktok_shop.factory_cli enqueue \
  --video data/tiktok_shop/clips/product_a_loop.mp4 \
  --product "Car phone mount"
```

**Post (spreads across accounts, max 10/day each):**

```bash
python3 -m shorts_bot.tiktok_shop.factory_cli post --confirm
python3 -m shorts_bot.tiktok_shop.factory_cli post-batch --max 5 --confirm
```

---

## How ban avoidance works here

- **10/day per account**, not 30 identical files on one account  
- **Different products + caption variants** in the queue  
- **loop-clip** = forward + reverse (not the same file posted twice)  
- **No "50% off"** text — bot strips `%` patterns from captions  

Ramp: first week OK to start at **5/day/account** — edit `daily_limit` in JSON.

---

## Autopilot (next)

Daily runner will: EchoTik scout → render → enqueue → post-batch until caps hit.  
For now: manual products + `enqueue` + `post-batch --max 10 --confirm` per account.

Log: `data/tiktok_shop/post_log.jsonl`  
Queue: `data/tiktok_shop/queue.json`
