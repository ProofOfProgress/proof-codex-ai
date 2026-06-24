# Priority list — reassess often

**North star (affiliate — owner 2026-06-24):** **100% AI-automated TikTok Shop affiliate** — faceless clips promoting trending Shop products, earn commission per sale.

**Owner decision:** Affiliate path. **Parked:** seller/Printify, GMV Max, YouTube RTR, Ms. Byte.

**Last assessed:** 2026-06-24

---

## Top 4

| # | Priority | Done when |
|---|----------|-----------|
| **1** | **Affiliate-eligible TikTok account(s)** | Can access Product Marketplace + add product links to posts |
| **2** | **First affiliate clip posted** | EchoTik product → Kling clip → live post with commission link |
| **3** | **3-account clip factory** | Up to 10 posts/day per account via bot + Zernio (different products/captions) |
| **4** | **Learn what converts** | Track sales by product; scout + clip winners harder |

---

## Follower reality (US, 2026)

| Followers | What you get |
|-----------|----------------|
| **0** | No Shop affiliate marketplace — must grow or acquire eligible account |
| **1,000+** | May enter **Creator Pilot** (limited: ~5 shoppable videos/week, high-rated shops only) |
| **5,000+** | Full **Affiliate Creator** marketplace access |

See `docs/FOR_OWNER_TIKTOK_AFFILIATE_START.md` for account options (grow vs buy — risks documented).

---

## Backlog (parked)

- TikTok Shop **Seller** + Printify + POD
- GMV Max ads (seller-only)
- YouTube / InVideo / horror Shorts
- Clipping marketplaces (different model — pay per view for famous people, not Shop commission)

---

## Bot commands

```bash
python3 -m shorts_bot.tiktok_shop.scout_cli run --preset middle_core --limit 10
python3 -m shorts_bot.tiktok_shop.factory_cli make-clip --product "Product name"
python3 -m shorts_bot.tiktok_shop.factory_cli post-batch --max 5 --confirm
```

Factory doc: `docs/FOR_OWNER_TIKTOK_SHOP_FACTORY.md`
