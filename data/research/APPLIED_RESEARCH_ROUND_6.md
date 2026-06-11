# Applied research — Round 6 (strengthen system)

**Date:** 2026-06-11

---

## System hardening

| Layer | Mechanism |
|-------|-----------|
| **Concurrency** | `pipeline_lock` — one `finish_cli` at a time (Replicate 429) |
| **Voice integrity** | `horror_guard` — auto-repair first-person drift pre/post humanize |
| **Artifact integrity** | `content_stamp` — stale I2V/VO cleared when script changes |
| **Quality** | `check_jenny_voice` wired into `run_quality_checks` as hard issue |
| **Upload** | Off-niche topic block (medieval/self-help); voided uploads excluded |
| **Ops** | `supervisor_cli --health` / `--run-once`; `queue_cli --health` |

---

## Config flags

- `pipeline_exclusive_lock` (default true)
- `pipeline_auto_horror_repair` (default true)
- `pipeline_block_voice_drift` (default true)

---

## Commands

```bash
python3 -m shorts_bot.production.supervisor_cli --health
python3 -m shorts_bot.production.supervisor_cli --run-once --no-upload
python3 -m shorts_bot.production.queue_cli --health
```
