# Launch priority matrix — July 2026

**How to read labels**

| Label | Meaning |
|-------|---------|
| **AI** | Cloud agent / automation only — no owner action |
| **Both (AI preferred)** | Owner can help, but agent should own it |
| **Both (human preferred)** | Agent prepares; owner must approve or do the sensitive step |
| **Human** | Owner only — money, logins, purchases, legal |

**North star:** First affiliate post **12:00 AM Launch Date** → **$1k commission in 7 calendar days** → **$500 bonus**.  
**Full step order:** `docs/LAUNCH_TODO.md` (sections A → I).

---

## P0 — Launch blockers (do these first)

| # | Task | Label | Status | Notes |
|---|------|-------|--------|-------|
| 1 | **Buy purchased TikTok Shop affiliate account** (~$630) | Human | ❌ | Section A3 — login + Shop access verified on phone |
| 2 | **Subscribe FastMoss** (~$59/mo) | Human | ❌ | Section A4 — replaces Kalodata/EchoTik for day-1 research |
| 3 | **Add `KALODATA_PILOT_TOKEN`** OR keep filtered Kalodata full-screen on hub Edge | Human | ❌ | Hands-off scout — [kalodata.com/pilot](https://www.kalodata.com/pilot) → Cursor Secrets → **new agent run** |
| 4 | **Scout 8–10 quality products** → `products.json` | Both (AI preferred) | ❌ Blocked on #3 or FastMoss API | Quality gate rejects junk; file is empty |
| 5 | **One end-to-end clip: QC pass + owner says “looks GOOD”** | Both (human preferred) | 🟡 Partial | Pipeline works; motion still weak on v1 — v2 Kling regen running |
| 6 | **Zernio subscription + `ZERNIO_API_TOKEN`** | Human | 🟡 Token OK | Confirm billing active (Section A6) |
| 7 | **Connect purchased account in Zernio** (defer until batch ready) | Both (human preferred) | ❌ | Section B — email/password only; never bot phone number |
| 8 | **Enable `affiliate_main` in `accounts.json`** with real Zernio ID | Both (AI preferred) | ❌ | Agent updates JSON after owner connects in Zernio |
| 9 | **Pick Launch Date + timezone + midnight plan** | Human | ❌ | Section H1 |
| 10 | **Build launch batch: 8–10 clips QC-pass + queued** | Both (AI preferred) | ❌ | Blocked on #4 and #5 |
| 11 | **Launch night: post #1 at 12:00 AM, then ≥30m spacing** | Both (AI preferred) | ❌ | Agent can tmux loop; owner on standby |

---

## P1 — Infrastructure already built (agent maintain)

| # | Task | Label | Status |
|---|------|-------|--------|
| 12 | Kalodata Playwright DOM scout (no coordinate misclicks) | AI | ✅ PR #170 |
| 13 | Per-product quality gate (≥8% comm, ≥$80, GMV ≥$10k, ≤200 creators) | AI | ✅ — cleared bad weekly-drop rows |
| 14 | Gemini visual critic + model routing (flash QC, lite scrape) | AI | ✅ PR #171 |
| 15 | Hub secrets sync (`sync_hub_agent_secrets.py`) | AI | ✅ Running |
| 16 | Pan-loop letterbox fix (cover-crop, no black pillarbox) | AI | ✅ Fixed today |
| 17 | Module 1 QC + inter-frame motion gate | AI | ✅ |
| 18 | Zernio on bubble + test accounts | AI | ✅ 4 TikTok accounts connected |
| 19 | Kling official API configured | AI | ✅ |
| 20 | Gemini API configured | AI | ✅ |

---

## P2 — Owner prep (parallel, not blocking code)

| # | Task | Label | Status |
|---|------|-------|--------|
| 21 | Confirm cash runway (~$2,283) | Human | ❓ |
| 22 | Confirm Kling / image credits | Human | ❓ |
| 23 | Skim Module 1, 3, 6, 7 + `PROMPT_BUILDER.md` | Human | ❌ Section D (~30 min) |
| 24 | Haircut / launch eve availability | Human | ❓ |
| 25 | Course $500 bonus proof rules | Human | ❓ |

---

## P3 — After products exist (agent-owned)

| # | Task | Label |
|---|------|-------|
| 26 | `factory_cli make-clip` × 8–10 products | Both (AI preferred) |
| 27 | Visual critic loop → prompt regen (max 2–3) | AI |
| 28 | `qc-batch --queue --account affiliate_main` | AI |
| 29 | Owner spot-check 3 random MP4s | Both (human preferred) |
| 30 | `factory_cli status` — queue pending 8–10 | AI |
| 31 | Discord / course intel ingest (background) | AI |

---

## P4 — Week 1 sprint (after first post)

| # | Task | Label |
|---|------|-------|
| 32 | 8–10 GOOD posts/day, ≥30m apart | Both (AI preferred) |
| 33 | Daily scout refresh + kill losers | Both (AI preferred) |
| 34 | Commission tracker (Section J table) | Both (human preferred) |
| 35 | Log wins in `GROUP_CALLS.md` | Both (human preferred) |

---

## What the agent did this session (AI-preferred work)

1. Fixed **pan-loop black bars** — `video_variants.py` now cover-crops instead of padding black.
2. Re-ran Module 1 QC on regen loop — **PASSED**.
3. Synced **Gemini secrets to hub**.
4. Tried **hub live Kalodata scrape** — screenshot OK; Gemini 503 / 0 rows (need pilot token or owner Kalodata on screen).
5. Started **Kling v2 regen** with stronger motion prompt (`bur_bur_mermaid_brush_v2.kling.txt`).
6. Upgraded **Gemini visual critic** (PR #171).

---

## Owner: three actions that unblock everything

1. **`KALODATA_PILOT_TOKEN`** in Cursor Secrets → start **new cloud agent** (or subscribe FastMoss + API keys).
2. **Buy purchased affiliate account** + confirm TikTok Shop works on your phone.
3. **Pick Launch Date** and tell the agent: *"Work section E from LAUNCH_TODO"*.

---

## Quick status command

```bash
python3 -m shorts_bot.tiktok_shop status
python3 -m shorts_bot.tiktok_shop.scout_cli validate
python3 -m shorts_bot.tiktok_shop.scout_cli ping
```
