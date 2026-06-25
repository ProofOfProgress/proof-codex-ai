# Applied research — Round 4

**Date:** 2026-06-11  
**Channel:** Don't Blink horror Shorts (AlphaBeta001)

---

## What we researched

| Priority | Finding | Applied |
|----------|---------|---------|
| I2V cost vs quality | When `ai_video_max_beats` < segment count, first N beats miss finale | `select_i2v_beat_indices()` — always hook + jumpscare |
| Jenny voice mismatch | `check_jenny_voice` required first-person; horror scripts are second-person | Horror lint: requires `you/your`, bans series numbering |
| Parallel Replicate 429 | Running draft 2+3 pipelines together stalls I2V | `queue_cli` — sequential approved queue |
| Ops visibility | Cloud agents need one-file launch snapshot | `ops_status_cli` → `data/OPS_STATUS.md` |
| Upload prep latency | Meta built only at end of pipeline | `queue_cli --prep-all-meta` for drafts 3–5 |

---

## Code shipped (Round 4)

- `shorts_bot/production/render_ai_video.py` — hook + finale beat priority
- `shorts_bot/production/jenny_checks.py` — second-person horror rules
- `shorts_bot/production/queue_cli.py` — list / prep-meta / run-next
- `shorts_bot/production/ops_status_cli.py` — OPS_STATUS generator
- Tests: `test_i2v_beat_selection.py`, `test_queue_cli.py`, updated `test_jenny_checks.py`

---

## Execution log

| Task | Status |
|------|--------|
| Video #1 LIVE (`-21Yc_xTcMY`) | Done (Round 2–3) |
| Draft #3 pipeline (security cam) | **In progress** — resume via `queue_cli --run-next` |
| Upload meta drafts 3–5 | Pre-built via `--prep-all-meta` |
| Draft #4 closet knock pipeline | Queued after #3 |
| Draft #5 wrong text pipeline | Queued after #4 |
| Studio rename Don't Blink | Owner — API forbidden |
| Pin CTA comment | Owner — Studio only |

---

## Next (Round 5 candidates)

1. Wire `visual_beats` from `data/draft_meta/` into `ai_video_prompts.py`
2. Draft #6 — photo timestamp (calendar Day 5)
3. Retention review Video #1 at 48h → feed `topic_rotation`
4. `script_humanize.py` prompt — purge cosy first-person LLM template
