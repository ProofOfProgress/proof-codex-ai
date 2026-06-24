# TikTok Shop Affiliate — what you do next

**Model:** Promote other brands’ products → earn commission. **Not** seller / Printify.

The bot scouts products and makes clips. **You need affiliate-eligible TikTok account(s) first.**

---

## The gate (read this)

| Followers | Can you do Shop affiliate? |
|-----------|----------------------------|
| **0** | ❌ No |
| **1,000+** | ⚠️ Pilot — ~5 shop videos/week |
| **5,000+** | ✅ Full product marketplace |

Full guide: **`docs/FOR_OWNER_TIKTOK_AFFILIATE_START.md`**

---

## Your options

1. **Grow** a TikTok to 1K/5K (safest, slow)  
2. **Buy** 1K or 5K account (fast, ban/scam risk — your call)  
3. Use an **existing** TikTok if you already have followers  

---

## Once Marketplace works on your phone

```bash
python3 -m shorts_bot.tiktok_shop.scout_cli run --preset middle_core --limit 10
python3 -m shorts_bot.tiktok_shop.factory_cli make-clip --product "Product name"
python3 -m shorts_bot.tiktok_shop.factory_cli post --confirm
```

**3 accounts:** copy `accounts.example.json` → `accounts.json`, fill Zernio IDs, ramp **3–5 posts/day** per account first.

---

## Parked (not this path)

Seller Center, Printify, GMV Max ads, own POD products.
