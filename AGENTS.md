# AGENTS.md — read this first (every new chat)

> **New cloud agent?** Run the bootstrap checklist: **`docs/CLOUD_AGENT_START.md`**  
> **Secrets added mid-chat?** Start a **new agent run** — this VM only gets secrets at launch.

## What this repo is

**TikTok Shop affiliate bot** — automation only. Connects APIs, generates clips, runs Module 1 QC, posts.

**Creative strategy lives in the course** — not in this codebase. ~90% of hooks, visuals, captions, growth, and compliance come from `data/research/course/`.

**Owner:** Not a developer. Plain English. One step at a time.

---

## What we are working on (2026)

| Track | When | Source |
|-------|------|--------|
| **Bubble wrap (NOW)** | Until ~1k followers per account | `BUBBLE_WRAP.md` + Drive samples |
| **Affiliate product videos** | After 1k | Course Modules 1, 3–8 |
| **Follow ads** | Later, 1k→5k | `ADS_1K_TO_5K.md` (deferred) |
| **Automation** | Always | `shorts_bot/tiktok_shop/` |

**North star:** TikTok Shop affiliate revenue via the owner's **Momentum Academy** course.

**Top 4:** `data/PRIORITIES.md` — work only those until reassessed.

---

## What is DEAD — never suggest or build

Do **not** pull creative direction from config defaults, old docs, or deleted code.

- Fix It Fast · Rapid Tool Review · Ms. Byte · InVideo daily workflow
- Peripheral horror YouTube · Jenny Codex strategist · AlphaBeta001 manager (legacy)
- Any deleted `archive/` content not re-ingested into `course/`

If you see these in code/comments, treat as legacy cruft. **Course wins.**

---

## Knowledge hierarchy

| Layer | Path | Covers |
|-------|------|--------|
| **Creative (~90%)** | `data/research/course/` | Product research, images, Kling video, editing, violations, appeals, growth |
| **Automation (~10%)** | `shorts_bot/tiktok_shop/` | EchoTik scout, Kling render, TikTok OAuth, Printify, Module 1 QC, queue |

Full index: `data/research/course/KNOWLEDGE.md` · Module list: `data/research/course/README.md`

**Owner overrides** (beat course when owner says so): `PROMPT_BUILDER.md`, `VIDEO_EDITOR.md`, `APPEALS.md`, `GROUP_CALLS.md`

---

## Affiliate video pipeline (course order)

1. **Module 1** — rules & violations (QC before every upload)
2. **Module 3** — pick product (EchoTik / research)
3. **Module 4** — AI image (ChatGPT Prompt Builder → Higgsfield/NanoBanana, 9:16, 2K)
4. **Module 5** — AI video (Kling 2.6, 5s, fixed arc-camera prompt, audio off)
5. **Module 6** — edit (~10s pan loop + pain-point caption, white box / black text)
6. **Module 7** — avoid violations (CTR ≥5%, no sale/price/discount words)
7. **Module 8** — appeals if flagged

**Mandatory QC:** `shorts_bot/tiktok_shop/module1_qc.py` — zero Module 1 violations or upload blocked.

---

## Commands

```bash
bash scripts/install.sh
python3 -m shorts_bot.tiktok_shop status
python3 -m shorts_bot.tiktok_shop.factory_cli make-clip --product "NAME"
python3 -m shorts_bot.tiktok_shop.factory_cli qc --video PATH --product NAME --caption "..."
python3 -m pytest tests/ -q
python3 -m shorts_bot.web   # http://127.0.0.1:8080/api/status
```

Owner setup: `docs/FOR_OWNER_BASICS.md` · Secrets: `docs/CURSOR_SECRETS.md`

---

## Code map

| Area | Path |
|------|------|
| Shop factory | `shorts_bot/tiktok_shop/` |
| Module 1 QC | `shorts_bot/tiktok_shop/module1_qc.py` |
| Pan loop edit | `shorts_bot/tiktok_shop/video_variants.py` |
| TikTok OAuth | `shorts_bot/tiktok/` |
| API config | `shorts_bot/config.py` |

---

## Cursor Cloud notes

- **No new Replicate I2V** unless owner asks (`AI_VIDEO_GENERATION_ENABLED=false` default).
- **Long jobs** (Kling, regen, QC): run in background; poll every 1–2 min.
- **Merge policy:** agents merge own PRs when tests pass and PR is MERGEABLE.
- **Group calls:** owner posts updates → log in `data/research/course/GROUP_CALLS.md`.
