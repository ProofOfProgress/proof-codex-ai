# 90-day blueprint — self-learning viral Shorts (on paper)

**Audience:** Owner (non-developer) + anyone asking “will this actually work?”  
**Honest line:** No system *guarantees* viral. This blueprint **engineers the conditions** for learn-and-improve — the same pattern used in production AI agents (public memory + evolution + closed feedback loops). Viral is an **outcome we measure and chase**, not a promise.

**Niche locked:** AI/tech product reviews · Pay / Skip / Wait · ~30s · **InVideo = production**

---

## The one-page story (what “bulletproof” means)

```
RESEARCH → SCRIPT → QC → INVIDEO → UPLOAD → ANALYTICS → LEARN → (repeat smarter)
     ↑__________________________________________________________|
```

Every arrow uses **either** our code **or** a named public library. Nothing depends on “hope.”

| Layer | Public / proven stack | Our role |
|-------|----------------------|----------|
| **Memory** | [Mem0](https://github.com/mem0ai/mem0) | What worked / failed persists across runs |
| **Evolution** | [TextGrad](https://github.com/zou-group/textgrad) (EvoAgentX engine) | Hook templates + workflow params improve from scores |
| **Orchestration** | Workflow JSON + telemetry (→ [Temporal](https://github.com/temporalio/temporal) later) | Daily loop steps versioned and auditable |
| **QC** | Gemini script gate (→ [DeepEval](https://github.com/confident-ai/deepeval) later) | Bad scripts never burn InVideo credits |
| **Production** | InVideo AI twin | Face + captions + b-roll — not homemade render |
| **Distribution** | YouTube Data + Analytics API | Upload + real performance signal |
| **Corrections** | Reflexio-style owner signals (built in) | “Framing wonky” → avoid rules + Mem0 |
| **Observability** | JSONL telemetry (→ [Langfuse](https://github.com/langfuse/langfuse) later) | Prove learning happened |

**Already merged:** Mem0, TextGrad, product queue (15), script QC, telemetry, workflow evolution, InVideo pipeline, YouTube upload.

---

## What “viral” means here (measurable)

We don’t optimize for vibes. We optimize for Shorts signals that **correlate with reach**:

| Signal | “Winning” threshold (adjust after 20+ uploads) | Learning action |
|--------|-----------------------------------------------|-----------------|
| Swipe-away rate | Lower than channel median | TextGrad rotates hook; Mem0 stores winner |
| Retention @ 3s | Above 70% | Repeat hook pattern + product format |
| Retention full | Above 50% on 30s | Repeat pacing / verdict timing |
| Views / 48h | Top quartile of last 10 | Double down topic + hook family |
| Comments / CTR | Rising | Queue more “vs” and “Pay or Skip” variants |

**Definition of success @ day 90:** Not “every video viral” — **at least 3 Shorts** clear the win thresholds **and** the system auto-reused their patterns on the next 10 without human rewriting.

---

## 90-day phases

### Days 1–30 · **Ship + signal** (learning needs data)

**Goal:** 10–15 public Shorts in the niche. Brain starts learning.

| Week | Owner / system | Public stack active |
|------|----------------|---------------------|
| 1 | Unblock hands: phone OR laptop Drive handoff | fetch_url + YouTube API |
| 2–4 | 1 Short / day when credits allow | InVideo + script QC + daily workflow |
| Ongoing | Analytics sync every 12h | RewardEngine → Mem0 + TextGrad |

**Exit criteria:** ≥10 uploads with analytics; hook templates evolved ≥2 times from real punish/reward.

**Blocker today:** InVideo credits + phone — use laptop export + Drive link until fixed.

---

### Days 31–60 · **Optimize loop** (public tools layer 2)

**Goal:** Win rate climbs; less manual fixing.

| Add (public) | Why |
|--------------|-----|
| **Langfuse** | Dashboard: “hook v7 beat v5 on ChatGPT Plus topic” |
| **DeepEval** | Script rubric: Pay/Skip/Wait clarity before InVideo |
| **Temporal** or **Prefect** | Daily loop survives crashes; retries are first-class |
| **Reflexio** (or expand owner_signals) | Every correction becomes training data |

**Exit criteria:** Median swipe-away down 20% vs first 10; ≥1 Short past internal “winner” threshold.

---

### Days 61–90 · **Scale what wins** (optional multi-surface)

**Goal:** Repeat winners; expand surface area.

| Add | Why |
|-----|-----|
| **TikTok / Reels API** | Same MP4, more reach (after phone OAuth) |
| **Postiz** (self-host) | Schedule cross-post from one upload |
| **EvoAgentX** (full) | Evolve full workflow topology, not just hooks |
| **A/B hooks** | Two templates per product; analytics picks |

**Exit criteria:** 3 documented winners; workflow version ≥10; queue auto-prioritizes product families that won.

---

## On-paper checklist (bulletproof criteria)

Use this to audit “will it self-learn?” — all must be **yes** by day 60:

- [ ] **Closed loop:** Upload → analytics → memory write → next script differs  
- [ ] **Versioned workflow:** Can show workflow v1 vs vN in telemetry  
- [ ] **No human in the daily path** (except paywall/credits — temporary)  
- [ ] **QC before spend:** Script QC blocks bad briefs  
- [ ] **Audit trail:** `data/telemetry/runs.jsonl` + Mem0 recall on demand  
- [ ] **Niche locked:** Product queue, not random topics  
- [ ] **Failure modes handled:** Credit fail → Drive fallback proposed; render retry ×2  

**Today (2026-06):** Run `python3 -m shorts_bot.learning.blueprint_audit` — expect **7/7 software yes**; daily path blocked only by InVideo credits/phone.

---

## Code traceability (claim → file)

| Claim | Where it lives |
|-------|----------------|
| Daily loop steps | `data/workflows/daily_invideo_v1.json` |
| Run orchestration | `shorts_bot/learning/workflow_runner.py` |
| Hook evolution (TextGrad) | `shorts_bot/learning/public_evolve.py` |
| Post-run + analytics evolution | `shorts_bot/learning/workflow_evolve.py` |
| Long-term memory (Mem0) | `shorts_bot/learning/mem0_bridge.py` |
| Script QC gate | `shorts_bot/learning/script_qc.py` |
| Run audit log | `shorts_bot/learning/run_telemetry.py` → `data/telemetry/runs.jsonl` |
| Owner corrections | `shorts_bot/learning/owner_signals.py` |
| Performance scoring | `shorts_bot/rewards/engine.py` |
| Analytics sync | `shorts_bot/youtube/sync.py` |
| InVideo production | `shorts_bot/invideo/` |
| Product queue (15) | `data/product_queue.json` |
| Blueprint self-check | `python3 -m shorts_bot.learning.blueprint_audit` |

---

## Risk register (honest)

| Risk | Impact | Mitigation (in repo) |
|------|--------|----------------------|
| InVideo credits / paywall | No new MP4s on cloud | Laptop export → Drive → `fetch_url_cli`; audit flags operational blocker |
| Phone / 2FA broken | Can't pay or TikTok OAuth | YouTube-only first; daily loop paused until resume |
| Viral not guaranteed | Revenue delay | Measure swipe-away + retention; evolve hooks from losers |
| TextGrad unavailable | Slower hook improvement | Template rotation fallback in `public_evolve.py` |
| Mem0 unavailable | Weaker cross-run memory | SQLite + agent memory still work |
| Browser download flake | Stuck before upload | Render retry ×2; Drive handoff path |

---

## Public tools roadmap (priority order)

| Priority | Tool | Status | Adds |
|----------|------|--------|------|
| P0 | Mem0 | ✅ Live | Long-term memory |
| P0 | TextGrad | ✅ Live | Hook / prompt evolution |
| P0 | YouTube Analytics API | ✅ Live | Reward signal |
| P1 | Langfuse | 🔜 | Prove learning visually |
| P1 | DeepEval | 🔜 | Bulletproof script QC |
| P1 | Temporal | 🔜 | Unkillable daily loop |
| P2 | Reflexio | 🔜 | Correction learning |
| P2 | Postiz | 🔜 | Cross-post |
| P3 | Full EvoAgentX | ⏸ | Full workflow autoconstruction |
| P3 | Exa / Firecrawl | ⏸ | Deeper product research |

---

## What we deliberately do NOT build

- Custom render stack (retired)  
- Custom memory from scratch (Mem0 instead)  
- Custom RL fine-tuning (TextGrad + rules instead)  
- “Virality ML model” day 1 (analytics thresholds + evolution first)

---

## Owner-facing one-liner

> **In 90 days the system doesn’t “hope” for viral — it posts daily, scores every Short, remembers what worked, and changes hooks and topics automatically. Public libraries do the hard AI parts; we own the YouTube + InVideo factory.**

---

## See also

- `docs/WORKFLOW_EVOLUTION.md` — how steps evolve  
- `docs/SYSTEM_UPGRADES.md` — what’s live now  
- `docs/PRIORITIES.md` — top 4 build order  
- `data/product_queue.json` — next 15 videos queued  
