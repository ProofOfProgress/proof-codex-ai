# Pipeline refinement — where coach input lands

**Purpose:** After a coach call, **every** part of the pipeline can change. This doc is the map.  
**Workflow:** Record → transcribe → extract rules → update files below → tests → one dry-run clip.

Owner does **not** need to edit code. Tell the CEO agent: **"Apply coach call refinements."**

---

## Refinement surfaces (all open)

| Stage | What coach might change | Where it gets encoded |
|-------|-------------------------|------------------------|
| **Product pick** | Filters, pre-breakout signals, red flags, commission bar | `PRODUCT_RESEARCH.md`, `GROUP_CALLS.md`, `data/tiktok_shop/products.json`, scout presets |
| **Module 4 image** | Backgrounds, settings, reference image use, staging | `PROMPT_BUILDER.md`, `module4_sample.py`, Gemini sample prompts, `product-video-prompt-builder` agent |
| **Module 5 video** | Motion wording, still-frame fix, parallax, Kling negatives | `.cursor/agents/product-video-prompt-builder.md`, `PROMPT_BUILDER.md` |
| **Module 6 edit** | Pan loop strength, caption style, white box rules | `VIDEO_EDITOR.md`, `video_variants.py`, `captions.py` |
| **Module 1 QC** | New bans, motion threshold, visual checks | `module1_qc.py`, `module_01_read_before_anything.md` |
| **Module 7 captions** | Banned words, CTR hooks | `captions.py`, `module1_qc.py`, `module_07_avoiding_violations.md` |
| **Module 8 appeals** | Wave playbooks | `APPEALS.md`, `GROUP_CALLS.md` |
| **Visual critic** | What "good enough" looks like | `video-visual-critic` agent instructions |
| **Research agent** | How scout ranks picks | `.cursor/agents/product-researcher.md`, scout_cli filters |

**Live overrides always beat stale docs:** `GROUP_CALLS.md` first, then owner files (`PROMPT_BUILDER.md`, `VIDEO_EDITOR.md`), then course modules.

---

## Post-call agent checklist (CEO runs this)

1. Transcribe recording → `data/research/course/inbox/coach-call-*-transcript.md`
2. Fill `inbox/coach-call-*.md` capture sections
3. Append dated section to **`GROUP_CALLS.md`**
4. Update every row in the table above that the coach touched
5. Add or adjust **QC gates** so the same mistake cannot ship twice
6. Run `pytest tests/` on touched areas
7. One **dry-run clip** proving the new rule (system dissection — not one-off MP4 patch)

---

## Learning loop (not "memory in chat")

| Layer | Role |
|-------|------|
| **Course modules** | Baseline textbook |
| **GROUP_CALLS.md** | Live coach truth |
| **SQLite agent memory + Mem0** | Promoted operating rules |
| **Code + QC** | Enforced gates — bot cannot ignore |

There is no single MCP that replaces this. **Files + QC + transcript pipeline = real learning.**

---

## Known refinement gaps (pre-call)

- Still-frame motion — coach law 2026-06-29 encoded; may need tuning after today
- Backgrounds too plain — need coach prompt samples for real environments
- FastMoss API — scout automation blocked until subscription/API; research rules still apply
- Product-researcher subagent — exists; will absorb research rules from today

See also: `docs/PIPELINE_SYSTEM_DESIGN.md`
