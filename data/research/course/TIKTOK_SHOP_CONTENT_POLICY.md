# TikTok Shop Content Policy — account defense brief

**Official source:** [TikTok Shop Content Policy](https://seller-sg.tiktok.com/university/essay?knowledge_id=7651420422014721&identity=1) (updated 2026-03-16)  
**Enforcement in bot:** `shorts_bot/tiktok_shop/tos_policy.py` + `module1_qc.py` (mandatory pre-upload)  
**Owner context:** One purchased affiliate account — **zero tolerance**. Repeated offenses escalate penalties.

This doc is written like a **defense memo**: what TikTok can enforce against us, and how we block it **before** post.

---

## How enforcement works (their “case”)

1. **Automated + human review** of video, caption, audio, listing match  
2. **Creator Performance Evaluation** — points, restrictions, bans on repeat  
3. **Appeals** via TikTok app — we preserve QC JSON (`data/tiktok_shop/module1_qc/`) as our diligence record  

**Our strategy:** never give them a clean violation on a single clip. Regen > post.

---

## 1. Product restrictions

| Policy | Risk to us | Defense |
|--------|------------|---------|
| **Prohibited / unsupported products** (weapons, drugs, Rx, tobacco, etc.) | Account strike if promoted | Module 3 — only list legitimate Shop products; scout/human block absurd categories |
| **Restricted products** without approval | Listing mismatch enforcement | Promote only the **exact** linked product |
| **Infant / follow-on formula (0–12 mo)** | Hard ban content | Never promote; vision QC flags formula |

---

## 2. Illegal, IP, gambling

| Policy | Risk | Defense |
|--------|------|---------|
| **Illegal activity** | Removal + account action | No criminal/glorifying content — N/A for product b-roll |
| **IP infringement** (logos, names, likeness without permission) | Strike + legal | Module 1: **only advertised product brand** in frame; vision QC flags Apple, Instagram, etc. |
| **Gambling / chance games** (spin wheel, lottery, lucky scoop, dice for prizes) | Strike | Caption QC bans: spin to win, raffle, lottery, roulette, jackpot, etc. |

---

## 3. Integrity & authenticity (highest risk for AI affiliate)

### Misleading or false content

| Policy | Risk | Defense |
|--------|------|---------|
| **Exaggerated claims** (health/beauty) | Misinformation strike | Caption QC: guaranteed, miracle, cure, FDA approved, clinically proven |
| **Misleading price / sale claims** | **#1 real-world strike** (Module 7) | Caption QC: sale, price, discount, coupon, free shipping, % off, BOGO, flash sale |
| **Auction / bidding** | Prohibited | Caption QC: bid, auction, going once |

### AIGC (AI-generated content)

| Policy | Risk | Defense |
|--------|------|---------|
| AIGC allowed if **Community Guidelines + this policy** | Strike if misleading | Course Rule 1: **disclose AI** on upload; prompts must not impersonate real people/brands |
| **Misleading / deceptive / impersonation AIGC** | Strike | Vision QC: no fake person, no counterfeit vibe, product must be real listing |
| **AIGC label** required per Community Guidelines | Metadata strike | Owner enables TikTok AIGC label at publish (Zernio/TikTok UI) |

### Giveaways & purchase incentives

| Policy | Risk | Defense |
|--------|------|---------|
| Giveaways / purchase incentives **unless official TikTok tools** | Strike | Caption QC: giveaway, free gift, comment to win, follow to win, buy to win |

### Redirecting traffic off-platform

| Policy | Risk | Defense |
|--------|------|---------|
| Links, **phone numbers**, social handles, email, QR → off-platform | Strike | Caption QC: URLs, @handles, emails, phone patterns, “link in bio”, WhatsApp, DM me |
| **Owner hard rule:** phone number **never** on bot account | Account + policy | No phone in secrets, captions, or overlays |

### Low-quality / unoriginal / non-interactive

| Policy | Risk | Defense |
|--------|------|---------|
| **Unoriginal** — repost, no new edit | Reach kill / strike | We generate unique Kling + pan loop per product — not reposts |
| **Non-interactive** — mostly stills, no activity | Low-quality flag | Arc camera pan loop (~10s), not static slideshow MP4 for affiliate |
| **Irrelevant promotional** — doesn’t show listed product | Strike | Vision QC: product 80%+ frame, must match listing |
| **Inconsistent product promotion** | Strike | One product per clip; QC product name matches listing |

---

## 4. Harmful & sensitive

| Policy | Risk | Defense |
|--------|------|---------|
| **Minors** promoting without adult | Strike | Module 1: no humans; vision QC flags minors |
| **Content directed to minors to buy** | Strike | No kid-targeted hooks for adult products |
| **Sexual content** in promotion | Strike | Module 1 + vision QC |
| **Weight management** — product **alone** causes loss/gain | Strike | Caption QC: lose weight, burn fat, fat burner; no weight-loss SKU unless fitness/lifestyle framing |
| **Sensational / shocking / violence** | Strike | Module 1 visual don’ts |
| **Political content** | Strike | Caption QC: vote, election, party names |
| **Sensitive events** exploitation | Strike | No disaster/profit hooks |

---

## 5. Fictitious listings

| Policy | Risk | Defense |
|--------|------|---------|
| Joke/meme/impossible products (“invisible phone”, “air for sale”) | Strike | Real FastMoss/Shop SKUs only |

---

## 6. Layered QC stack (our “brief” for appeals)

Every affiliate upload runs:

1. **Text QC** — `tos_policy.check_promotional_text()` on caption + description  
2. **Posting rules** — spacing, duplicate product, daily cap (Module 1)  
3. **Duration** — minimum 7s  
4. **Vision QC** — Module 1 course don’ts **+** `TOS_VISION_VIOLATIONS` via Gemini  
5. **Saved report** — timestamped JSON for appeal evidence  

```bash
python3 -m shorts_bot.tiktok_shop.factory_cli qc \
  --video PATH --product "NAME" --caption "..." --account affiliate_main
```

**Upload blocked** unless violations = 0.

---

## 7. What we still do manually at publish

- **AIGC disclosure toggle** in TikTok (Course Rule 1)  
- **Correct product link** in Shop showcase  
- **Appeals** via Module 8 if false positive — use saved QC report  

---

## 8. Priority order (one account bet)

1. **No misinformation words** (sale/price/discount) — Module 7 + TOS  
2. **Product clearly shown** — irrelevant/low-quality  
3. **No off-platform redirect** — especially phone/email/URL  
4. **No third-party logos** — IP  
5. **No giveaway/gambling language**  
6. **Module 1 visual don’ts** — water, screens, humans, etc.  

When in doubt: **regenerate**, do not post.

---

## Related

- Course Module 1: `module_01_read_before_anything.md`  
- Course Module 7: `module_07_avoiding_violations.md`  
- Appeals: `APPEALS.md`  
- Code: `shorts_bot/tiktok_shop/tos_policy.py`
