# TikTok Shop factory — faceless product clips

**Start with 1 account.** One seller-linked TikTok → **3–5 product videos/day** on **your** listings.

The old “3 accounts × 10/day” plan was for **affiliate** spam across multiple TikToks. **Seller path** = one official shop TikTok (0 followers OK). Scale volume later with **affiliates** posting for you, not 3 of your own accounts on day one.

No character. No VO. Short sale-style captions.

---

## What you need first (one-time)

1. **TikTok Shop Seller account** (0 followers OK) — see `docs/FOR_OWNER_TIKTOK_SELLER_START.md`
2. **Printify** connected in Seller Center (POD)
3. **EchoTik API** — bot scouts product ideas (see `docs/FOR_OWNER_ECHOTIK_SETUP.md`)
4. **Kling credits** — bot renders 1080p clips
5. **Zernio** (optional autopost) OR post manually from the queue

---

## Configure accounts (one is enough)

```bash
cp data/tiktok_shop/accounts.example.json data/tiktok_shop/accounts.json
```

Edit `data/tiktok_shop/accounts.json` — **only `shop_1` needs to be filled** to start:

| Field | What to put |
|-------|-------------|
| `id` | `shop_1` |
| `daily_limit` | `5` to start (ramp to 10 later) |
| `zernio_account_id` | From zernio.com for your **seller** TikTok |
| `post_via` | `zernio` or post manually |

Disable or delete `shop_2` / `shop_3` until you open a **second shop** (different brand) on purpose.

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

**Download product images + refresh cover URLs:**

```bash
python3 -m shorts_bot.tiktok_shop.factory_cli prep-images --force
```

**Kling render (one product):**

```bash
python3 -m shorts_bot.tiktok_shop.factory_cli render --product "Car phone mount"
python3 -m shorts_bot.tiktok_shop.factory_cli make-clip --product "Car phone mount"
```

`make-clip` = render + loop + enqueue in one step.

**Make ~10s clip from 5s Kling export (manual):**

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
