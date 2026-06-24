# TikTok Shop Seller — start here (0 followers OK)

Plain steps for opening a **seller** account and connecting Printify. This matches the guru course we ingested (Jon Reiter / TikTokWiz).

---

## Step 1 — Seller Center signup

1. Go to **https://seller-us.tiktok.com**
2. Click **Sign up** → **Individual seller** (not business unless you have an LLC)
3. Use **email + password** (easier account recovery than Google login)
4. Complete: legal name, US address, ID, SSN, bank account
5. Pick a **broad shop name** (ChatGPT is fine — e.g. “Home Finds US”)

**Do not** set your home address as the warehouse if you use Printify (Step 2).

---

## Step 2 — Printify (POD)

1. **https://printify.com** → create account → **Premium** plan (better margins)
2. In TikTok Seller Center: **Connect Printify** (Apps / Service providers)
3. In Printify: set **default print provider** and pickup warehouse to **Printify Fort Worth** (see guru transcript for exact address flow)
4. Keep **$100–$1,000** in your card/bank for POD — Printify charges when orders ship, before TikTok pays you

---

## Step 3 — Link TikTok app

1. Seller Center → **Official account** → **Link TikTok account**
2. Scan QR code with the TikTok app on your phone
3. Confirm: **shop bag icon** appears on your TikTok profile
4. Test: create a draft video → you should be able to **tag a product**

You do **not** need 1K or 5K followers for seller-linked product videos.

---

## Step 4 — First product (manual once)

Guru method: find a winner on TikTok Shop tab → validate in EchoTik/Kalodata → copy or twist design → list on Printify → publish to Shop.

Bot helps with **EchoTik scout**:

```bash
python3 -m shorts_bot.tiktok_shop.scout_cli run --preset middle_core --limit 10
python3 -m shorts_bot.tiktok_shop.scout_cli list
```

For **POD**, you’ll create your own designs (funny shirts, gift niches) — scout is for research, not copy-paste listings.

---

## Step 5 — Faceless videos (bot)

After Kling credits + scout:

```bash
python3 -m shorts_bot.tiktok_shop.factory_cli prep-images --force
python3 -m shorts_bot.tiktok_shop.factory_cli make-clip --product "your product name"
python3 -m shorts_bot.tiktok_shop.factory_cli post --confirm
```

Target: **3–5 videos/day** on your seller TikTok to warm the listing before pushing affiliates.

---

## Step 6 — Affiliates + ads (later)

1. Seller Center → **Affiliate program** → open collaboration → **30% commission** on winners
2. Message creators who already sell similar products
3. After consistent sales: **GMV Max** ads in Seller Center (start small — $20–50/day test)

---

## Owner checklist file

Short version: **`data/tiktok_shop/OWNER_NEXT_STEPS.md`**

Factory commands: **`docs/FOR_OWNER_TIKTOK_SHOP_FACTORY.md`**
