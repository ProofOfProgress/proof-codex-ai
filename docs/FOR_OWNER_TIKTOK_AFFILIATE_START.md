# TikTok Shop Affiliate — start here

**What affiliate means:** You promote **someone else’s** TikTok Shop product in a short video. When someone buys through your link, **you get commission** (often 15–30%). No store, no Printify, no shipping.

**What the bot does:** Finds hot products (EchoTik) → makes faceless 1080p clips (Kling) → queues posts.

---

## Step 0 — You need an eligible TikTok (this is the gate)

You **cannot** do Shop affiliate with a brand-new 0-follower account in the US.

| Your situation | What TikTok allows |
|----------------|-------------------|
| **0 followers** | ❌ No affiliate marketplace |
| **1,000–4,999** | ⚠️ **Pilot program** — ~5 shoppable videos/week, limited shops (95%+ rating) |
| **5,000+** | ✅ Full affiliate marketplace |

**Check on your phone:** TikTok → **Profile → TikTok Studio / Creator Center** → look for **TikTok Shop** or **Product Marketplace**.

---

## Three ways to get eligible

### Option A — Grow (safest, slowest)

- Pick **one niche** (beauty, gadgets, supplements, home)
- Post daily non-shop content until **1K**, then apply for pilot / keep growing to **5K**
- Timeline: weeks to months

### Option B — Buy an account (fast, risky)

People buy **aged** or **1K/5K follower** accounts to skip the grind.

**Only consider if you accept:**

- Against TikTok rules → **ban** = lost account + unpaid commission  
- **Scams** — seller reclaims account  
- Must match **US + ID verification** to your identity when TikTok asks  
- **Warm slowly** — don’t post 30 videos day one on a fresh login  

**If you buy, minimum checklist:**

- US account, **good standing**, no prior shop bans  
- **1K+** for pilot, **5K+** for full access  
- Email/login you control; change password immediately  
- Use **one device/IP** consistently at first  
- Start **3–5 posts/day**, not 30  

We **don’t** recommend vendors or automate purchases — too much scam surface. Owner decision.

### Option C — Seller invite (Marketing Creator)

A **seller** can invite you with **no follower minimum** — but someone else has to invite you to *their* shop. That’s not “pick any product in the marketplace.” Usually not how faceless factories scale.

---

## Affiliate business flow (once eligible)

```
EchoTik scout → pick product with good commission + sales
     ↓
Bot makes 1080p faceless clip
     ↓
You post on TikTok with PRODUCT LINK (Shop affiliate tag)
     ↓
Viewer buys → TikTok pays you commission
```

**You are not the advertiser.** You are the **promoter**. Brands set commission; you drive traffic.

---

## Multi-account factory (why 3 accounts)

Original plan: **3 TikToks × up to 10 videos/day each** = spread volume, avoid hammering one account.

Rules:

- **Different products** per post (scout gives variety)  
- **Different captions** (bot variants)  
- **Not** the same file posted 30 times identically  
- Ramp: start **3–5/day/account**, increase after no warnings  

Configure:

```bash
cp data/tiktok_shop/accounts.example.json data/tiktok_shop/accounts.json
# Fill shop_1, shop_2, shop_3 with Zernio IDs (or post manually)
```

---

## Daily commands

```bash
python3 -m shorts_bot.tiktok_shop.scout_cli run --preset middle_core --limit 10
python3 -m shorts_bot.tiktok_shop.scout_cli list
python3 -m shorts_bot.tiktok_shop.factory_cli make-clip --product "Product name"
python3 -m shorts_bot.tiktok_shop.factory_cli status
python3 -m shorts_bot.tiktok_shop.factory_cli post --confirm
```

---

## Money math (realistic)

- Commission example: $25 product × 20% = **$5 per sale**  
- Most clips get **few views** — need **volume** (many clips × many products)  
- One viral clip + high-commission product = good day; most days = small or zero  

---

## vs Seller (why you chose affiliate)

| | **Affiliate (you)** | **Seller (parked)** |
|---|---------------------|---------------------|
| Own products? | No | Yes (Printify) |
| Followers needed? | **Yes (1K–5K)** | 0 for seller shop |
| Inventory? | None | POD float |
| Bot fit | **Strong** — scout + clip other people’s products | Strong for *your* listings |

---

## Next step for you

1. **Get one affiliate-eligible TikTok** (grow, buy, or use existing if you have one)  
2. Turn on **TikTok Shop affiliate** in app + verify ID  
3. Tell me when Marketplace works → we scout + `make-clip` + post  

Full factory doc: `docs/FOR_OWNER_TIKTOK_SHOP_FACTORY.md`
