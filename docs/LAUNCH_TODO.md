# Launch to-do list — in order

**Do these top to bottom.** Check each box before moving on.  
**Last step = LAUNCH** (first upload). That starts your **7-day $1k clock**.

---

## North star

| Goal | Reward |
|------|--------|
| **$1,000 commission** in the **first 7 days** after **first upload** | **$500** course bonus |

**Chase math:** ~**$143/day** average commission across 7 days. Course peers hit **$100 days in a week** — this is the target, not a fantasy.

**What counts as day 0:** the moment the **first affiliate video goes live** on the purchased account (Zernio post confirmed).

**Not day 0:** scout runs, dry-run renders, QC tests, bubble posts, inbox drafts.

---

## How to use this doc

- **Owner steps** — you buy, log in, approve products, watch videos once.
- **Agent steps** — cloud agent runs commands, renders, QC, queues posts.
- **Together** — product pick approval, spot-check finalists, green-light launch batch.

Bubble wrap (4 phones, laptop hub) is **parallel** — it does **not** appear in this list because it does **not** block affiliate launch.

---

## Section A — Money & account *(owner)*

### A1. Haircut
- [ ] Done (~$20–40). Stop delaying.

### A2. Confirm cash
- [ ] ~**$2,283** on hand (or updated number written here: $_______)

### A3. Buy purchased affiliate TikTok account (~$630)
- [ ] Account purchased from trusted seller  
- [ ] You have **login** (email/phone + password)  
- [ ] Account has **TikTok Shop affiliate** access (not just a normal TikTok)  
- [ ] Note follower count / age / any flags: _______________  
- [ ] Log in once on **your phone** — confirm no instant ban, showcase loads  

**Stop if:** account locked, no Shop access, or seller won't prove login.

### A4. Pay EchoTik (~$125/mo)
- [ ] Upgrade at [echotik.live](https://echotik.live) — paid tier active  
- [ ] Credentials in **Cursor Cloud Agent → Secrets** (`ECHOTIK_USERNAME`, `ECHOTIK_PASSWORD`)  
- [ ] **Rotate password** if it was ever pasted in chat  

### A5. Confirm Kling / image billing
- [ ] Kling credits or Replicate billing active (`KLING_ACCESS_KEY` + `KLING_SECRET_KEY` or `REPLICATE_API_TOKEN`)  
- [ ] Higgsfield or ChatGPT image path ready for Module 4 stills  
- [ ] `KLING_MODE=std` (~$0.21/5s) unless you have a reason for pro  

### A6. Confirm Zernio
- [ ] Zernio subscription active  
- [ ] `ZERNIO_API_TOKEN` in Cursor Secrets  

**Section A done when:** account in hand + EchoTik paid + Kling/Zernio funded.

---

## Section B — Wire affiliate account *(owner + agent)*

### B1. Connect purchased account in Zernio dashboard
- [ ] Owner: Zernio → **Connect TikTok** → log in as **purchased account**  
- [ ] Copy new Zernio **account ID**  

### B2. Update bot config
- [ ] Agent: paste ID into `data/tiktok_shop/accounts.json` → `affiliate_main.zernio_account_id`  
- [ ] Set `affiliate_main.enabled` → `true`  
- [ ] Set label to real username (replace "TBD")  

### B3. Sync secrets on cloud VM
```bash
bash scripts/install.sh
python3 -m shorts_bot.cloud_secrets
python3 -m shorts_bot.zernio.auth_cli
```
- [ ] `affiliate_main` shows in Zernio account list  
- [ ] All three commands run clean  

**Section B done when:** purchased account appears in Zernio + config enabled.

---

## Section C — Green-light all APIs *(agent)*

Run and fix until green:

```bash
bash scripts/install.sh
python3 -m shorts_bot.tiktok_shop status
python3 -m shorts_bot.tiktok_shop.scout_cli status
python3 -m shorts_bot.tiktok_shop.scout_cli ping
```

- [ ] **EchoTik:** configured — ping returns data (not "Usage Limit Exceeded")  
- [ ] **Kling:** configured  
- [ ] **Zernio:** configured  
- [ ] **affiliate_main:** enabled, remaining = 10/day  

**Section C done when:** status + ping green, affiliate account ready to receive posts.

---

## Section D — Course refresh *(owner — 30 min)*

Skim before you pick products (creative = course, not bot defaults):

- [ ] `module_01_read_before_anything.md` — violations list  
- [ ] `module_03_product_research_strategies.md` — what makes a good product  
- [ ] `module_06_editing.md` + `VIDEO_EDITOR.md` — pan loop + caption  
- [ ] `module_07_avoiding_violations.md` — **no sale/price words**, CTR ≥5%  
- [ ] `PROMPT_BUILDER.md` — image + Kling prompt style  

**Section D done when:** you know what "GOOD" looks like before launch.

---

## Section E — Scout product batch *(agent + owner)*

### E1. Run EchoTik scout
```bash
python3 -m shorts_bot.tiktok_shop.scout_cli run --preset middle_core --limit 15
python3 -m shorts_bot.tiktok_shop.scout_cli run --preset two_hundred --limit 10
python3 -m shorts_bot.tiktok_shop.scout_cli list
```
- [ ] `data/tiktok_shop/products.json` has **10–15 candidates**  

### E2. Owner spot-check top 5–8 *(course Module 3)*

For each finalist, verify (Kalodata or seller page if needed):

- [ ] **6+ of 10** top affiliate vids show purple **ad** badge (brand ad spend)  
- [ ] **Revenue trend** rising — skip flat/down  
- [ ] **Brand match** — image, title, shop name align  
- [ ] **Commission $** worth it (price × rate)  
- [ ] **Creator variety** — not only brand self-promo  

- [ ] Owner **approves 8–10 products** for launch batch (write names):  
  1. _______________  
  2. _______________  
  3. _______________  
  4. _______________  
  5. _______________  
  6. _______________  
  7. _______________  
  8. _______________  
  9. _______________ (optional)  
  10. _______________ (optional)  

**Section E done when:** 8–10 approved products locked — no launch without this.

---

## Section F — Dry run: one clip, zero upload *(agent)*

Prove pipeline before the launch batch:

```bash
python3 -m shorts_bot.tiktok_shop.factory_cli prep-images
python3 -m shorts_bot.tiktok_shop.factory_cli make-clip --product "FIRST_APPROVED_PRODUCT_NAME"
python3 -m shorts_bot.tiktok_shop.factory_cli qc --video PATH_FROM_OUTPUT --product "NAME" --caption "CAPTION"
```

- [ ] Product image downloaded  
- [ ] Kling 5s render OK  
- [ ] Pan loop + caption burn OK  
- [ ] **Module 1 QC = 0 violations**  
- [ ] Owner **watched the MP4** — looks course-quality (product scale, lighting, no motion bugs)  

If QC fails: **regen** — do not lower standards for speed.

**Section F done when:** one perfect clip exists and owner said yes to the look.

---

## Section G — Build launch batch *(agent)*

Produce **8–10 QC-pass clips** — one per approved product (or 2 clips on your best 4 products if you want depth on winners).

For each approved product:
```bash
python3 -m shorts_bot.tiktok_shop.factory_cli make-clip --product "PRODUCT_NAME"
python3 -m shorts_bot.tiktok_shop.factory_cli qc --video PATH --product "NAME" --caption "CAPTION" --account affiliate_main
python3 -m shorts_bot.tiktok_shop.factory_cli enqueue --video PATH --product "NAME" --caption "CAPTION" --account affiliate_main
```

- [ ] Clip 1 — QC pass — queued  
- [ ] Clip 2 — QC pass — queued  
- [ ] Clip 3 — QC pass — queued  
- [ ] Clip 4 — QC pass — queued  
- [ ] Clip 5 — QC pass — queued  
- [ ] Clip 6 — QC pass — queued  
- [ ] Clip 7 — QC pass — queued  
- [ ] Clip 8 — QC pass — queued  
- [ ] Clip 9 — QC pass — queued *(optional)*  
- [ ] Clip 10 — QC pass — queued *(optional)*  

```bash
python3 -m shorts_bot.tiktok_shop.factory_cli status
```
- [ ] **Queue pending: 8–10**  
- [ ] All captions: **no** sale / price / discount / coupon / free shipping words  
- [ ] All videos: **AI disclosure** handled per Module 1  
- [ ] Spacing plan: posts **≥30 minutes apart** (Module 1) — schedule batch accordingly  

**Section G done when:** 8–10 clips queued, every one QC-clean, owner spot-checked at least 3 random clips.

---

## Section H — Pre-launch final check *(owner + agent)*

- [ ] Purchased account still healthy in TikTok app  
- [ ] Zernio shows affiliate account connected  
- [ ] Showcase / affiliate links work on the account  
- [ ] You know how to read **TikTok Shop affiliate earnings** (where $1k is tracked)  
- [ ] Course **$500 bonus rules** confirmed (who to notify, proof needed): _______________  
- [ ] Write **launch timestamp plan** — when first post goes live: _______________  

**Section H done when:** everyone agrees the batch is GOOD and you're ready to start the clock.

---

## Section I — 🚀 LAUNCH *(agent — last step before week 1 sprint)*

**This is the last item on the pre-launch list.**  
**First `--confirm` post = day 0. 7-day $1k clock starts now.**

Post launch batch to **affiliate_main** only:

```bash
python3 -m shorts_bot.tiktok_shop.factory_cli post --account affiliate_main --confirm
# repeat every ≥30 min until daily cap, OR:
python3 -m shorts_bot.tiktok_shop.factory_cli post-batch --max 10 --confirm
```

- [ ] **First video live** — record URL + time: _______________  
- [ ] **Day 0 date/time locked:** _______________ (**7-day deadline:** _______________)  
- [ ] Remaining launch-day posts going out (8–10 total, ≥30m apart)  
- [ ] `factory_cli status` shows posts sent on `affiliate_main`  

**LAUNCH COMPLETE** when 8–10 affiliate videos are **live** on the purchased account.

---

## Section J — Week 1 sprint: chase $1k *(days 1–7 after first upload)*

**Target:** **$1,000 commission** by end of day 7 → **$500 bonus**.

### Daily loop (every day, days 1–7)

| Time | Action |
|------|--------|
| **Morning** | Check overnight earnings + CTR on yesterday's posts |
| **Scout** | `scout_cli run` — refresh products if winners/losers clear |
| **Produce** | 8–10 new **GOOD** clips (or double down on winning product) |
| **QC** | Module 1 zero violations on every clip |
| **Post** | 8–10/day on `affiliate_main`, ≥30m apart |
| **Evening** | Log commission total + note which product/video drove sales |

### Rules for the sprint

- [ ] **Never skip QC** to hit volume — one violation can kill the week  
- [ ] **Kill losers fast** — low CTR products get dropped same day  
- [ ] **Double winners** — if one product sells, make more angles same day  
- [ ] **No misinformation words** — Module 7 (no fake sales/discounts)  
- [ ] Track running total daily (below)  

### Commission tracker

| Day | Date | Posts sent | Est. commission today | Running total | Notes |
|-----|------|------------|----------------------|---------------|-------|
| 0 | | 8–10 (launch) | $ | $ | first upload |
| 1 | | | $ | $ | |
| 2 | | | $ | $ | |
| 3 | | | $ | $ | |
| 4 | | | $ | $ | |
| 5 | | | $ | $ | |
| 6 | | | $ | $ | |
| 7 | | | $ | $ | **$1k? → claim $500** |

- [ ] **Hit $1,000** running total within 7 days of first upload  
- [ ] Submit proof per course rules → **collect $500 bonus**  

---

## Section K — After week 1 *(don't stop)*

- [ ] Keep **8–10 GOOD posts/day** — course cadence until Platinum  
- [ ] Log wins in `data/research/course/GROUP_CALLS.md`  
- [ ] Bubble hardware + phone hub when budget allows (`docs/FOR_OWNER_PHONE_HUB.md`) — growth track, not revenue blocker  

---

## Quick command reference

| Task | Command |
|------|---------|
| Full status | `python3 -m shorts_bot.tiktok_shop status` |
| EchoTik ping | `python3 -m shorts_bot.tiktok_shop.scout_cli ping` |
| Scout | `python3 -m shorts_bot.tiktok_shop.scout_cli run --preset middle_core --limit 15` |
| One clip | `python3 -m shorts_bot.tiktok_shop.factory_cli make-clip --product "NAME"` |
| QC | `python3 -m shorts_bot.tiktok_shop.factory_cli qc --video PATH --product NAME --caption "..."` |
| Queue | `python3 -m shorts_bot.tiktok_shop.factory_cli enqueue --video PATH --product NAME --caption "..." --account affiliate_main` |
| Post one | `python3 -m shorts_bot.tiktok_shop.factory_cli post --account affiliate_main --confirm` |
| Post batch | `python3 -m shorts_bot.tiktok_shop.factory_cli post-batch --max 10 --confirm` |

---

## Related docs

| Doc | Purpose |
|-----|---------|
| `LAUNCH_BUDGET.md` | Cash / runway math |
| `LAUNCH_CHECKLIST.md` | Short strategy summary |
| `FOR_OWNER_ECHOTIK_SETUP.md` | EchoTik secrets |
| `FOR_OWNER_ZERNIO_SETUP.md` | Zernio hookup |
| `FOR_OWNER_KLING_SETUP.md` | Kling billing |
| `PRODUCT_RESEARCH.md` | Scout + manual checks |
| `module_01` … `module_08` | Course creative rules |

**Agents:** tell the cloud agent *"Work down `docs/LAUNCH_TODO.md` — we're on section ___"*.
