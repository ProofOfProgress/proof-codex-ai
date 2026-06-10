# Autonomous AI self-training research — applied to Shorts Bot (2026)

Deep research synthesis on **autonomous self-training** for LLM agents, mapped to Soft Continuity’s existing rule-learning stack.

**Sources:** [Memento 2 / Stateful Reflective Memory](https://arxiv.org/pdf/2512.22716), [Dual-Process self-evolving agents (MDPI 2026)](https://www.mdpi.com/2079-9292/15/6/1232), [Agent Evolving Learning (AEL)](https://arxiv.org/pdf/2604.21725), [Experiential Reinforcement Learning](https://arxiv.org/pdf/2602.13949), codebase audit (`SELF_LEARNING.md`, `feedback.py`, `extensions.py`).

---

## Executive summary

| Question | Answer for Shorts Bot |
|----------|----------------------|
| **Is this ML fine-tuning?** | **No** — we keep the LLM frozen; learning = memory writes + prompt injection |
| **What pattern fits?** | **Dual-process:** fast System 1 (draft/upload) + slow System 2 (sync reflection) |
| **Core loop** | Experience → reflection → consolidation → retrieve on next draft |
| **What we added** | Episodic memory, rule confidence, upload attribution, draft→improvement bridge, LEARNED.md read-back |

---

## Research patterns (2025–2026)

### 1. Reflective memory (Memento / SRDP)
Policy improvement via **retrieval over episodic memory**, not gradients. Experiences are written back with evaluative feedback; future actions condition on structured recall.

**Applied:** `learning_episodes` table + `recent_episode_reflections()` in `applied_training_context()`.

### 2. Dual-process agents (DPA)
- **System 1:** answer/draft using compact retrieved context  
- **System 2:** after each episode, audit trace → conservative memory delta writes  

**Applied:** `reflect_after_sync()` runs after analytics sync in `coordinator.py`.

### 3. Experience–reflection–consolidation (ERL)
Attempt → feedback → structured reflection → refined behavior → **internalize** so deployment does not need reflection at inference.

**Applied:** Draft feedback creates improvement proposals auto-approved → `applied:*` rules; validated rules promote to `agent_memories` after N reward hits.

### 4. Diagnose before prescribe (AEL)
Slow window: LLM diagnoses *why* performance changed before structural changes.

**Applied:** Offline reflection strings tie verdict + diagnosis + upload topic; demote rules after 2+ punishes.

---

## Architecture (implemented)

```
┌─────────────────────────────────────────────────────────────┐
│ SYSTEM 1 (fast)                                             │
│ Draft approve/reject → avoid/repeat + improvement proposal  │
│ Upload → snapshot active rules on upload_events             │
│ DraftGenerator / Agent ← applied_training_context()         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ SYSTEM 2 (slow) — after analytics sync                      │
│ RewardEngine → reflect_after_sync()                         │
│   • Match video ↔ upload (title/video_id)                   │
│   • bump_rule_confidence (+reward / −punish)                │
│   • Write learning_episodes                                 │
│   • Demote rules confidence < 35% after 2 punishes          │
│   • Promote validated rules → agent_memories                │
└─────────────────────────────────────────────────────────────┘
```

---

## Storage

| Table / file | Role |
|--------------|------|
| `learning_episodes` | Episodic reflections (sync + draft) |
| `rule_confidence` | Per-rule confidence, reward/punish hits, promoted flag |
| `upload_events.active_rules_json` | Causal snapshot at upload time |
| `training_config` | `applied:*`, `avoid:*`, `repeat:*`, `rejected:*` |
| `agent_memories` | Long-term promoted rules (`source=self_training`) |
| `data/LEARNED.md` | Human audit + **now read back** into training context |

---

## Config

```env
SELF_TRAINING_ENABLED=true
SELF_TRAINING_PROMOTE_THRESHOLD=2
```

---

## What is still NOT autonomous ML

- No weight updates / fine-tuning / RLHF on the base model  
- No A/B experiment IDs on uploads (future)  
- Neutral videos still produce no proposals  
- Reflection text is template-based offline (LLM reflection optional future)

---

## Commands

- `sync` — triggers full loop including self-training reflection  
- Draft Yes/No — immediate learning + episodic write + auto improvement when safe  
- `python3 -m shorts_bot.memory.memory_cli list` — see promoted rules  

---

## Verdict

Shorts Bot now implements **autonomous reflective self-training** in the agent-memory sense: it observes outcomes, consolidates lessons, validates rules against performance, and promotes durable rules into strategist memory — without retraining the LLM.
