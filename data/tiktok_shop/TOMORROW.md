# Tomorrow — call + TikTok unlock

**You:** Rest. Show up to the call with questions only — no buying on the spot.

**Bot (done tonight):** Scout refreshed, vertical 9:16 clip fix, queue cleaned, this checklist.

---

## Your call (questions only)

Full list: `data/tiktok_shop/CALL_PREP.md`

**Must ask:**

1. Account has **Shop Marketplace** working — not just followers?  
2. **1K vs 5K** — what do I need?  
3. **Refund** if banned in 30 days?  
4. Safe **posts per day** on a fresh login?  
5. EchoTik vs Charm for product scouting?

**Do not commit.** Say: *"I'll follow up after I compare."*

---

## After the call — tell the bot

- Price for one account  
- Refund policy  
- 1K or 5K recommendation  
- Gut check: scam y/n  

---

## When TikTok Shop unlocks

1. Check **Creator Center → TikTok Shop** on your phone  
2. If affiliate works (or after you buy account):  
   ```bash
   python3 -m shorts_bot.tiktok_shop.scout_cli list
   python3 -m shorts_bot.tiktok_shop.factory_cli make-clip --product "Product name"
   python3 -m shorts_bot.tiktok_shop.factory_cli post --confirm
   ```

---

## Stockpile (optional — uses Kling credits)

Bot can pre-render clips from tonight's scout list so you post fast once an account is live. Say *"render top 3"* if you want that tomorrow.
