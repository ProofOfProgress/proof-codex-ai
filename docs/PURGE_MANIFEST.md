# Purge manifest — Peripheral → AI/Tech pivot

**Date:** 2026-06  
**Principle:** Delete or archive anything that only served horror/Peripheral homemade video. Keep money path: scripts → InVideo → upload → analytics → memory.

---

## KEEP (core infrastructure)

| Area | Path / module | Why |
|------|---------------|-----|
| YouTube | `shorts_bot/youtube/` | Upload + OAuth + analytics — works |
| Upload CLIs | `upload_canonical_cli`, `upload_meta`, compliance | Distribution |
| Drafts / scripts | `shorts_bot/drafts/` | Repurpose prompts for AI/tech |
| Agent memory | `shorts_bot/memory/`, `data/MEMORY.md` | Slim + dedupe, keep system |
| Codex search | `shorts_bot/codex/` | Repurpose BM25 for AI/tech research |
| Web UI | `shorts_bot/web/` | Ops dashboard |
| Manager | `shorts_bot/agents/` | AlphaBeta001 |
| Self-learning | `shorts_bot/rewards/`, `shorts_bot/training/` | Wire after uploads flow |
| Closed loop shell | `closed_loop_cli.py` | Replace render step with InVideo |
| Config / secrets | `shorts_bot/config.py`, `scripts/sync_secrets.py` | |
| Tests (non-horror) | Most of `tests/` | Update niche/world tests |

---

## ARCHIVE (move to `archive/peripheral/` — not daily path)

| Area | Examples |
|------|----------|
| Horror research | `HORROR_*.md`, jumpscare JSON, PERIPHERAL_* |
| Brand bible | `channel/brand/world.md`, `horror_lane.md`, `identity.md` (Peripheral) |
| Launch horror playbooks | `data/LAUNCH_QUALITY.md` (horror-specific sections) |
| Creature / env assets | `channel/assets/creatures/`, gas station env |
| Horror draft JSON | `the-village-sign-*.json` |

---

## DEPRECATE — Phase 2 code removal (after InVideo wired + tests updated)

Do **not** delete in one shot — imports and tests still reference these.

| Module | Reason |
|--------|--------|
| `shorts_bot/production/blender/` | Homemade 3D — abandoned |
| Recraft / Replicate I2V | `render_ai_images`, `images/recraft*`, `render_ai_video` |
| Kling pipeline | `render_kling`, `kling_setup_cli` |
| TurboScribe browser sync | Broken audio-first path |
| Horror-specific | `horror_guard`, `horror_lane`, `horror_sfx_mix`, `scare_pillar`, `world.py`, `micro_jumpscare_render` |
| Lost Boy / Recraft labs | `lost_boy_image_lab`, `recraft_setup_cli` |
| Resemble horror VO | `tts/horror_voice`, `edge_horror` — InVideo voice replaces |
| Meta/Facebook (optional) | Keep in repo but deprioritize until YouTube prints |

**Phase 2 gate:** `PIPELINE_BACKEND=invideo` ships one Short end-to-end → then delete deprecated modules + fix tests.

---

## REWRITE (this PR)

| File | Action |
|------|--------|
| `docs/PRIORITIES.md` | InVideo + upload + daily loop |
| `docs/CHANNEL_NICHES.md` | AI/tech hierarchy |
| `shorts_bot/production/niche.py` | New DEFAULT_TOPICS + positioning |
| `AGENTS.md` | Remove Peripheral north star |
| `data/operating_rules_seed.md` | InVideo default, horror rules out |
| `data/MEMORY.md` | Dedupe duplicate Codex entries |

---

## DO NOT PURGE

- `data/youtube_token.json` — live auth
- `course/files/` — Jenny Codex still useful for hooks/retention (adapt, don't worship)
- SQLite DB — draft history + analytics
- InVideo research — `data/research/INVIDEO_NICHE_PIVOT_RESEARCH.md` (recreate if missing on branch)
