# TikTok Shop Content Policy — zero-strike prevention brief

**North star:** **Never get a strike.** Block risky clips before upload — regen until clean. Do **not** post and plan to appeal.

**Official source:** [TikTok Shop Content Policy](https://seller-sg.tiktok.com/university/essay?knowledge_id=7651420422014721&identity=1) (updated **2026-03-16**)  
**Enforcement in bot:** `shorts_bot/tiktok_shop/tos_policy.py` + `module1_qc.py` (mandatory pre-upload)  
**Owner context:** One purchased affiliate account. TikTok states **repeated offenses → more significant penalties**. Treat every category as one-strike fatal.

Module 8 / `APPEALS.md` = emergency fallback only if TikTok false-flags a QC-passed clip — **not the strategy**.

---

## How TikTok enforces (what we never trigger)

1. **Automated + human review** — video, caption, audio, listing match  
2. **Creator Performance Evaluation** — points, restrictions, escalating penalties on repeat  
3. **One purchased account** — no room for “we’ll appeal it later”

**Our strategy:** Map every policy section to a **pre-upload block**. If QC fails → regen. If unsure → do not ship.

---

## Section map — policy → prevention → code

### A. Restrictions on products you can promote

| Policy (2026-03-16) | Strike risk | Our prevention | Gate |
|---------------------|-------------|----------------|------|
| **Prohibited / unsupported** — weapons, drugs, tobacco, Rx, sexual enhancement, hazardous goods | Removal + account action | Module 3: real Shop SKUs only; block absurd categories in scout | Research + vision QC |
| **Restricted products** without seller approval | Listing mismatch / enforcement | Promote **exact** linked product only | `--product` must match listing |
| **Infant formula (0–6 mo)** | Hard ban | Never promote | Vision QC |
| **Follow-on formula (6–12 mo)** | Hard ban | Never promote | Vision QC |

### B. Illegal, IP, gambling

| Policy | Strike risk | Our prevention | Gate |
|--------|-------------|----------------|------|
| **Illegal / criminal activity** | Removal + account action | Product b-roll only — no criminal glorification | Vision QC |
| **IP infringement** — brands, logos, likeness without permission | Strike + legal | **Only advertised product brand** in frame (owner override 2026-06-28) | Module 1 + vision QC |
| **Gambling / chance gamification** (spin wheel, lottery, dice-for-prizes) | Strike | Ban chance language in caption; no wheel/lottery visuals | `GAMBLING_PHRASES` + vision |

### C. Integrity & authenticity (highest risk for AI affiliate)

| Policy | Strike risk | Our prevention | Gate |
|--------|-------------|----------------|------|
| **Misleading / false content** | Misinformation strike | Pain-point hooks only — no false promises | Caption QC |
| **Exaggerated claims** (health / beauty) | Misinformation | No guaranteed, miracle, cure, FDA, clinically proven | `EXAGGERATED_CLAIM_PHRASES` |
| **Misleading price / sale claims** | **#1 real-world affiliate strike** (Module 7) | No sale, price, discount, coupon, free shipping, % off, BOGO | `MISINFORMATION_PHRASES` |
| **Auction / bidding** (incl. external auction redirects) | Strike | No bid / auction language | `AUCTION_PHRASES` |
| **AIGC allowed** when not misleading + **AIGC label** required | Metadata / authenticity strike | Unique Kling gen per clip; **owner enables AIGC label at publish**; no impersonation | Prompt builder + publish checklist |
| **Misleading / impersonation AIGC** | Strike | No fake people, no counterfeit vibe, real listing product | Vision QC + Module 5 prompts |
| **Artificial engagement / spam** | Strike | No follow-for-follow, buy likes/followers, engagement bait | `ARTIFICIAL_ENGAGEMENT_PHRASES` |
| **Giveaways / purchase-based incentives** (unless official TikTok tools) | Strike | No giveaway, free gift, comment/follow/buy to win | `GIVEAWAY_PHRASES` + `PURCHASE_INCENTIVE_PHRASES` |
| **Redirect off-platform** — URL, phone, email, @handle, QR | Strike | Regex + phrase block; **phone never on bot account** | `REDIRECT_*` |
| **Simulcasting / multicasting** (same live on multiple platforms) | Strike | **N/A** — we post pre-recorded MP4s, not simultaneous live | — |
| **Unoriginal content** — repost, no new edit | Reach kill / strike | Every clip = new Kling + pan loop — never repost | Pipeline design |
| **Pre-recorded / not real-time** (low-quality bucket) | Low-quality flag | Policy allows if **new creative edit** added — our arc pan loop + unique AI gen satisfies this | Pan loop + motion QC |
| **Non-interactive** — mostly stills, no activity | Low-quality flag | ~10s arc camera pan loop — not static slideshow | Vision: arc_camera check |
| **Irrelevant promotional** — wrong product / not shown | Strike | Product 80%+ frame, matches listing | Vision QC |
| **Inconsistent product promotion** | Strike | One product per clip; name matches listing | QC `--product` + vision |
| **Fictitious listings** — joke / meme / impossible goods | Strike | Real FastMoss/Shop SKUs only | Module 3 + vision |

### D. Harmful & sensitive

| Policy | Strike risk | Our prevention | Gate |
|--------|-------------|----------------|------|
| **Minors under 18** promoting without adult | Strike | No humans in affiliate clips | Module 1 + vision |
| **Content directed to minors to buy** | Strike | No kid-targeted hooks on adult SKUs | Agent judgment + vision |
| **Sexual content** in promotion | Strike | Module 1 visual don’ts | Module 1 + vision |
| **Sexual enhancement products** (prohibited category) | Hard ban | Never promote; caption + vision block | Research + QC |
| **Weight management** — product **alone** causes loss/gain | Strike | No lose weight / burn fat / fat burner hooks unless fitness/lifestyle SKU | `WEIGHT_MANAGEMENT_PHRASES` |
| **Sensational / shocking / violence** | Strike | Module 1 visual don’ts | Vision QC |
| **Political content** | Strike | No vote / election / party hooks | `POLITICAL_PHRASES` |
| **Sensitive events** exploitation (disasters, crises for profit) | Strike | No disaster/tragedy profit hooks | `SENSITIVE_EVENTS_PHRASES` + vision |

---

## Pre-upload checklist (never skip)

Every affiliate clip:

1. **Text QC** — `tos_policy.check_promotional_text()` on caption + description  
2. **Posting rules** — spacing, duplicate product, daily cap (Module 1)  
3. **Duration** — minimum 7s  
4. **Vision QC** — Module 1 course don’ts **+** `TOS_VISION_VIOLATIONS` via Gemini  
5. **Saved report** — timestamped JSON audit trail (`data/tiktok_shop/module1_qc/`)

```bash
python3 -m shorts_bot.tiktok_shop.factory_cli qc \
  --video PATH --product "NAME" --caption "..." --account affiliate_main
```

**Upload blocked** unless violations = **0**.

---

## Publish checklist (manual — still strike prevention)

These are **not** optional nice-to-haves; missing them is strike risk:

| Step | Why |
|------|-----|
| **AIGC label ON** in TikTok publish UI | Required per Community Guidelines for AI video |
| **Correct Shop product link** attached | Irrelevant / inconsistent promotion |
| **Caption matches listing truth** | Misinformation if viewer clicks and offer differs |
| **No phone / email / URL in post metadata** | Redirect off-platform |

---

## Priority order (one account bet)

1. **No misinformation words** (sale / price / discount) — Module 7 + TOS  
2. **Product clearly shown** — irrelevant / low-quality / inconsistent  
3. **No off-platform redirect** — especially phone / email / URL  
4. **No third-party logos** — IP  
5. **No giveaway / gambling / purchase-incentive language**  
6. **Module 1 visual don’ts** — water, screens, humans, etc.  
7. **AIGC label at publish** — authenticity metadata  

When in doubt: **regenerate**, do not post.

---

## What TikTok says about breaches (context only)

> “If you are found to violate these guidelines, you may have enforcement actions taken against your account… repeated offenses will result in more significant penalties.”

Appeals exist in the app — we **do not plan to use them**. Prevention is the only acceptable path for this account.

---

## Related

- Course Module 1: `module_01_read_before_anything.md`  
- Course Module 7: `module_07_avoiding_violations.md`  
- Code: `shorts_bot/tiktok_shop/tos_policy.py`  
- Emergency only: `APPEALS.md` · `module_08_beating_violations.md`
