# Fix It Fast — TikTok Shop setup (plain English)

**Goal:** Sell physical gadgets through TikTok Shop Shorts. Brand locked: **Fix It Fast**.

---

## Step 1 — TikTok Shop seller account (you, once)

1. Open **TikTok Seller Center** (seller-us.tiktok.com or your region)
2. Create seller account — ID, tax, payout bank
3. List your first products (or connect a supplier catalog)
4. Match listings to `data/product_queue.json` (car gap filler, jar grip, etc.)

---

## Step 2 — TikTok upload API (for bot posting)

Follow `docs/FOR_OWNER_TIKTOK_SETUP.md` — developer app, OAuth, test upload.

Until audit passes, posts may be **private** — that's normal.

---

## Step 3 — Pin Shop product on each Short

When you post (or when bot posts), **attach the Shop product link** so the orange cart appears.

No link = views but no sales.

---

## Step 4 — Daily ship (bot)

On laptop with Cursor open, use `/loop` from `docs/FOR_OWNER_LOOP.md` — or run:

```bash
python3 -m shorts_bot.production.invideo_daily_cli
```

Each run: next gadget from queue → InVideo demo video → upload.

---

## Product hopping

- Test product → if no sales after fair tries, **drop it**
- Winner → make 3–5 more hooks for same SKU
- Queue always has next product ready in `data/product_queue.json`

---

## What we don't do

- AI software affiliate reviews (retired)
- Rapid Tool Review / Ms. Byte (archived)
- TikTok Shop without listing products first
