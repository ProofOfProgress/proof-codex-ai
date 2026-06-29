# Launch to-do list — in order

**Do these top to bottom.** Check each box before moving on.  
**Last step = LAUNCH** (first upload). That starts your **7-day $1k clock**.

---

## North star

| Goal | Reward |
|------|--------|
| **$1,000 commission** in **7 calendar days** (Launch Date → Launch Date + 6 days) | **$500** course bonus |

**Chase math:** ~**$143/day** average commission across 7 days. Course peers hit **$100 days in a week** — this is the target, not a fantasy.

**What counts as day 0:** the moment the **first affiliate video goes live** on the purchased account (Zernio post confirmed).

**Launch timing (owner rule):** first video goes live at **12:00 AM (midnight)** on the **Launch Date** you pick — start of the calendar day so you get **7 full days** to earn (not a 3pm start that wastes half of day 1).

**Not day 0:** scout runs, dry-run renders, QC tests, bubble posts, inbox drafts.

---

## Launch calendar *(fill in Section H)*

| Field | Your value |
|-------|------------|
| **Launch Date** | _______________ |
| **Timezone** | _______________ *(your local — used for midnight)* |
| **First post** | **12:00 AM** on Launch Date |
| **Bonus deadline** | **11:59 PM** on Launch Date **+ 6 days** *(7 calendar days — no nitpicking)* |
| **Posts 2–10 launch day** | Every **≥30 min** after first post (~4.5 hrs for 10 posts → done ~4:30 AM) |

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

### A4. Subscribe FastMoss (~$59/mo Basic — verify on site)
- [ ] Account at [fastmoss.com](https://www.fastmoss.com/) — **replaces EchoTik + Kalodata**
- [ ] Optional API: [developers.fastmoss.com](https://developers.fastmoss.com/) → `FASTMOSS_CLIENT_ID` + `FASTMOSS_CLIENT_SECRET` in Cursor Secrets
- [ ] **Do not pay EchoTik**

### A5. Confirm Kling / image billing
- [ ] Kling credits or Replicate billing active (`KLING_ACCESS_KEY` + `KLING_SECRET_KEY` or `REPLICATE_API_TOKEN`)  
- [ ] Higgsfield or ChatGPT image path ready for Module 4 stills  
- [ ] `KLING_MODE=std` (~$0.21/5s) unless you have a reason for pro  

### A6. Confirm Zernio
- [ ] Zernio subscription active  
- [ ] `ZERNIO_API_TOKEN` in Cursor Secrets  

**Section A done when:** account in hand + **FastMoss subscribed** + Kling/Zernio funded.

---

## Section B — Wire affiliate account *(owner + agent — **defer until closer to launch**)*

**Owner rule (2026-06-29):** Do **not** connect purchased account to Zernio during warmup. Wire **only when owner says launch is close** (typically after Section G queue is ready).

**Phone rule:** Purchased account **phone number never** goes to bot, secrets, or automation. Zernio login = **email + password only** when you connect.

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

- [ ] **FastMoss:** subscribed (app); API optional until scout ships  
- [ ] **Kling:** configured  
- [ ] **Zernio:** configured  
- [ ] **affiliate_main:** enabled, remaining = 10/day  

**Section C done when:** status + ping green, affiliate account ready to receive posts.

---

## Section D — Course refresh *(owner — 30 min)*

Skim before launch batch clips (creative = course, not bot defaults):

- [ ] `module_01_read_before_anything.md` — violations list  
- [ ] `module_03_product_research_strategies.md` — what makes a good product  
- [ ] `module_06_editing.md` + `VIDEO_EDITOR.md` — pan loop + caption  
- [ ] `module_07_avoiding_violations.md` — **no sale/price words**, CTR ≥5%  
- [ ] `PROMPT_BUILDER.md` — image + Kling prompt style  

**Section D done when:** you know what "GOOD" looks like before launch.

---

## Section E — Scout product batch *(agent — owner does not pick)*

### E1. Agent runs FastMoss research

**Owner does not pick products** (`GROUP_CALLS.md` 2026-06-29). CEO delegates **`product-researcher`** or runs scout when API + subscription active. Apply **pre-breakout lens** (rising GMV before saturation).

```bash
python3 -m shorts_bot.tiktok_shop.scout_cli run --preset middle_core --limit 15
python3 -m shorts_bot.tiktok_shop.scout_cli list
python3 -m shorts_bot.tiktok_shop.scout_cli report
```

- [ ] **8–10 products locked** in `data/tiktok_shop/products.json` (agent-run scout / product-researcher)

**Section E done when:** 8–10 products in `products.json` with pre-breakout lens — no launch without this.

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
- [ ] Spacing plan: post **#1 at 12:00 AM** Launch Date; posts **#2–10 every ≥30 minutes** — **do not** `post-batch` all at once  
- [ ] Launch batch **fully queued before 11 PM** the night before Launch Date  

**Section G done when:** 8–10 clips queued, every one QC-clean, owner spot-checked at least 3 random clips.

---

## Section H — Pre-launch final check *(owner + agent)*

### H1. Pick Launch Date + midnight plan

- [ ] **Launch Date chosen:** _______________  
- [ ] **Timezone written down:** _______________  
- [ ] **Bonus deadline** (Launch Date + 6 days, 11:59 PM): _______________  
- [ ] Owner + agent **available at 11:55 PM** the night before Launch Date (or stay up)  
- [ ] Phone alarm **11:55 PM** launch eve; second alarm **12:00 AM**  

**Why midnight:** posting at noon on Monday only gives you half of Monday + 6 days. Posting at **12:00 AM Monday** gives **all of Mon–Sun** to hit $1k.

### H2. Ready-to-fire checklist

- [ ] Purchased account still healthy in TikTok app  
- [ ] Zernio shows affiliate account connected  
- [ ] Showcase / affiliate links work on the account  
- [ ] **8–10 clips queued** — verified `factory_cli status` shows pending queue  
- [ ] You know how to read **TikTok Shop affiliate earnings** (where $1k is tracked)  
- [ ] Course **$500 bonus rules** confirmed (who to notify, proof needed): _______________  

**Section H done when:** Launch Date locked, batch queued, midnight plan understood, everyone on standby.

---

## Section I — 🚀 LAUNCH *(agent — last step before week 1 sprint)*

**This is the last item on the pre-launch list.**  
**First live post at 12:00 AM Launch Date = Day 1. 7 calendar days to $1k.**

### Launch night timeline

| Time (Launch Date) | Action |
|--------------------|--------|
| **11:55 PM** *(eve)* | Final `factory_cli status` — queue has 8–10 pending |
| **12:00 AM** | **Post #1** — starts the bonus clock |
| **12:30 AM** | Post #2 |
| **1:00 AM** | Post #3 |
| **… every 30 min …** | Posts #4–10 |
| **~4:30 AM** | Launch day batch done (if 10 posts) |

### Commands — one post at a time (Module 1 spacing)

**Do not** use `post-batch --max 10` at midnight — that ignores the 30-minute rule.

```bash
# 12:00 AM — post #1 ONLY
python3 -m shorts_bot.tiktok_shop.factory_cli post --account affiliate_main --confirm

# Wait ≥30 minutes, then repeat for #2, #3, … until 8–10 live or daily cap hit
python3 -m shorts_bot.tiktok_shop.factory_cli post --account affiliate_main --confirm
```

Agent can run a **30-minute loop** in tmux until launch-day batch is out, or owner runs each post manually.

### Launch checklist

- [ ] **Post #1 live at 12:00 AM** — record URL + exact timestamp: _______________  
- [ ] **Day 0 locked:** _______________ **Deadline:** _______________  
- [ ] Posts #2–10 spaced ≥30m through early morning  
- [ ] `factory_cli status` shows **8–10 sent** on `affiliate_main` for launch day  

**LAUNCH COMPLETE** when launch-day batch is live and the **12:00 AM first post** timestamp is logged.

---

## Section J — Week 1 sprint: chase $1k *(days 1–7 after first upload)*

**Target:** **$1,000 commission** by **11:59 PM on Launch Date + 6 days** → **$500 bonus**.

**Daily posting window:** after launch night, aim for **8–10 new posts spread through each day** (not all at midnight every day — that was launch night only).

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

| Day | Calendar date | Posts sent | Est. commission today | Running total | Notes |
|-----|---------------|------------|----------------------|---------------|-------|
| 1 | *(Launch Date)* | 8–10 from 12:00 AM | $ | $ | midnight = clock start |
| 2 | | | $ | $ | |
| 3 | | | $ | $ | |
| 4 | | | $ | $ | |
| 5 | | | $ | $ | |
| 6 | | | $ | $ | |
| 7 | | | $ | $ | **$1k? → claim $500 by 11:59 PM** |

- [ ] **Hit $1,000** running total by **11:59 PM on Launch Date + 6 days** (7 calendar days)  
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
| FastMoss ping | `python3 -m shorts_bot.tiktok_shop.scout_cli ping` |
| Scout | `python3 -m shorts_bot.tiktok_shop.scout_cli run --preset middle_core --limit 15` |
| One clip | `python3 -m shorts_bot.tiktok_shop.factory_cli make-clip --product "NAME"` |
| QC | `python3 -m shorts_bot.tiktok_shop.factory_cli qc --video PATH --product NAME --caption "..."` |
| Queue | `python3 -m shorts_bot.tiktok_shop.factory_cli enqueue --video PATH --product NAME --caption "..." --account affiliate_main` |
| Post one | `python3 -m shorts_bot.tiktok_shop.factory_cli post --account affiliate_main --confirm` |
| Post batch | `post-batch` — **not for launch night** (use spaced single posts) |

---

## Related docs

| Doc | Purpose |
|-----|---------|
| `LAUNCH_BUDGET.md` | Cash / runway math |
| `LAUNCH_CHECKLIST.md` | Short strategy summary |
| `FOR_OWNER_FASTMOSS_SETUP.md` | FastMoss subscription + API secrets |
| `FOR_OWNER_ZERNIO_SETUP.md` | Zernio hookup |
| `FOR_OWNER_KLING_SETUP.md` | Kling billing |
| `PRODUCT_RESEARCH.md` | Scout + manual checks |
| `module_01` … `module_08` | Course creative rules |

**Agents:** tell the cloud agent *"Work down `docs/LAUNCH_TODO.md` — we're on section ___"*.
