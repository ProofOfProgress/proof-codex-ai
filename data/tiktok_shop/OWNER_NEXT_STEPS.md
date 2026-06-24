# TikTok Shop — what you do next (tired-owner checklist)

**We committed to TikTok Shop seller (2026-06-24).** This is the only business we're building. Clipping, YouTube, and character content are parked.

The bot handles scouting, clips, captions, and posting. You only need to finish setup once.

---

## Tonight (15–30 min)

1. **Add Kling credits** — https://app.klingai.com → buy a small pack (~$10 test).  
   Without balance, `make-clip` stops with “Account balance not enough.”

2. **Sign up as a Seller** (0 followers OK) — https://seller-us.tiktok.com  
   Choose **Individual seller**. Use email login (not Google). Have ID + SSN + bank ready.

3. **Connect Printify** — https://printify.com → Premium → link TikTok Shop in Seller Center.  
   Keep ~$100–$1K float for POD charges (Printify bills before TikTok pays you).

4. **Link your TikTok** — Seller Center → link official account (QR code on phone).

---

## When Kling has credits (bot commands)

Open a terminal in the project folder and run:

```bash
python3 -m shorts_bot.tiktok_shop.factory_cli status
python3 -m shorts_bot.tiktok_shop.factory_cli prep-images --force
python3 -m shorts_bot.tiktok_shop.factory_cli make-clip --product "Speak Love"
```

That scouts products → Kling 5s pan video → loops to ~10s → adds to post queue.

Dry-run post (no upload):

```bash
python3 -m shorts_bot.tiktok_shop.factory_cli post
```

Real upload (after Zernio + accounts.json):

```bash
python3 -m shorts_bot.tiktok_shop.factory_cli post --confirm
```

---

## Still needed for autopost

| Item | Where |
|------|--------|
| Zernio connected TikTok(s) | zernio.com dashboard |
| `data/tiktok_shop/accounts.json` | copy from `accounts.example.json`, fill Zernio IDs |
| Rotate Kling key | you pasted it in chat — regenerate at app.klingai.com |

---

## What the bot already has

- EchoTik product scout (daily winners)
- Cover URL parsing + Kling render pipeline
- Caption variants (no “% off” spam)
- 10/day per account quota + queue

---

## Model we’re following

**Seller path** (Jon Reiter / TikTokWiz course): you own the listing, post faceless clips, recruit affiliates at ~30%, scale with GMV Max.  
Not the “5K follower affiliate-only” path.

Full playbook: `data/research/TIKTOK_SHOP_GURU_PLAYBOOK.md`  
Seller setup guide: `docs/FOR_OWNER_TIKTOK_SELLER_START.md`
