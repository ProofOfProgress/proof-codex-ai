# Launch prep brief — where we are

**North star:** **$1,000 commission** in **7 calendar days** from **12:00 AM Launch Date** → **$500 course bonus**.

**Ordered checklist:** `docs/LAUNCH_TODO.md` · **Pipeline:** `docs/PIPELINE_SYSTEM_DESIGN.md`

*Updated from repo + owner session — adjust checkboxes as you complete steps.*

---

## Critical path (affiliate — blocks midnight launch)

Nothing else on this list matters until these are done **in order**:

| Step | LAUNCH_TODO | Status | Owner / agent |
|------|-------------|--------|---------------|
| **A3** | Buy affiliate account (~$630) | ⬜ **Not done** | **Owner** |
| **A4** | EchoTik paid (~$125/mo) | ⬜ Trial exhausted — need paid | **Owner** |
| **A5–A6** | Kling + Zernio funded | 🟡 Zernio likely OK; confirm Kling billing | **Owner** |
| **B** | Connect account in Zernio → `affiliate_main` | ⬜ Waiting on A3 | Owner + **agent** |
| **C** | `status` + `scout_cli ping` green | ⬜ After A4 | **Agent** |
| **D** | Course refresh (30 min) | ⬜ Owner skim Modules 1,3,6,7 | **Owner** |
| **E** | Scout + approve **8–10 products** | ⬜ | Agent + **owner** |
| **F** | Dry run: 1 clip, QC pass, owner watches | ⬜ | **Agent** |
| **G** | Queue **8–10** QC-pass clips | ⬜ | **Agent** |
| **H** | Pick **Launch Date** + timezone + midnight plan | ⬜ | **Owner** |
| **I** | **LAUNCH** — post #1 at **12:00 AM**, #2–10 every ≥30m | ⬜ Last step | **Agent** |

**Clock does not start until Section I post #1 is live.**

---

## Parallel track (does NOT block affiliate)

| Item | Status | Notes |
|------|--------|-------|
| HP laptop + Ubuntu 26.04 | 🟡 In progress (long install) | Bubble hub + remote SSH later |
| 4 phones + SIMs + hub | ⬜ Not bought | ~$280 when ready |
| Phone hub worker | ⬜ Not built | Mackenzie automation |
| Bubble posts | ⬜ | 4 Zernio accounts wired in config |
| Tailscale + agent SSH | ⬜ | After Ubuntu opens — `FOR_OWNER_REMOTE_HUB_SSH.md` |

---

## Already in place (automation + docs)

| Done | Detail |
|------|--------|
| ✅ | Module 1 QC gate (`module1_qc.py`) |
| ✅ | Factory CLI: scout, render, make-clip, qc, enqueue, post |
| ✅ | 4 bubble accounts in Zernio (`accounts.json`) |
| ✅ | EchoTik client + scout CLI (needs paid tier) |
| ✅ | Agent team + mission log (`agent_ops`) |
| ✅ | Knowledge Gatherer (`/knowledge-gather`) |
| ✅ | Launch budget, todo, midnight rules, pipeline design |
| ✅ | Cursor project rules (`.cursor/rules/*.mdc`) |

---

## Owner: do these while Ubuntu installs

1. **Buy affiliate account** (~$630) — single biggest blocker  
2. **Pay EchoTik** — echotik.live upgrade  
3. **Confirm Kling/Replicate billing** has a payment method  
4. **Pick Launch Date** — first midnight post (give agent 48h+ after account for batch prep if possible)  
5. **Write timezone:** _______________  
6. **Skim** Module 1 + 7 (violations / no sale words) — 20 min  

---

## Agent: ready when owner says "account bought"

```bash
bash scripts/install.sh
python3 -m shorts_bot.tiktok_shop status
python3 -m shorts_bot.tiktok_shop.scout_cli ping
```

Then Sections **B → C → E → F → G** per `LAUNCH_TODO.md`. CEO follows `docs/PIPELINE_SYSTEM_DESIGN.md` + `.cursor/rules/ceo-orchestration.mdc`.

---

## Launch night reminder

- Post **#1 at 12:00 AM** Launch Date  
- Posts **#2–10** every **≥30 minutes** — **no** `post-batch` at midnight  
- **7 calendar days** to $1k — deadline **11:59 PM** on Launch Date + 6 days  

---

## Cash reminder

~$2,283 cash · ~$760–910 to open (account + stack day 1) · full ~$500/mo from first post. See `LAUNCH_BUDGET.md`.
