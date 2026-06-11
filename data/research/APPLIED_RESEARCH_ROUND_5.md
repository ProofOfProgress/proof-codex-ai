# Applied research — Round 5 (improve)

**Date:** 2026-06-11

---

## Problems fixed

| Issue | Root cause | Fix |
|-------|------------|-----|
| Upload guard false block | Erroneous medieval upload counted in 24h window | `voided` flag on `upload_events`; auto-void `JIkMhPH0l6o` |
| Draft #3 first-person VO | `script_humanize` still used cosy first-person LLM prompt | Horror humanize prompt + `horror_repair` + draft #3 repaired |
| I2V prompts ignored storyboard | `visual_beats` only in manifest, not prompts | Wired into `build_image_briefs` + `build_video_prompt_briefs` |
| Hook template mismatch | Segment 0 used keyword match only | `match_template(segment_index=0)` prefers hook role |
| Upload description slop | Research `competitor_gap` leaked into viewer description | Removed; `_normalize_horror_hook()` for second-person |
| Queue opacity | No clip progress | `queue_cli --list` shows `clips/target` |

---

## Shipped

- `upload_guard_void_video_ids` + voided upload filtering
- `horror_repair.py` + `queue_cli --repair-draft`
- `visual_beat_for_segment()` in `drafts/meta.py`
- Draft **#6** approved (photo timestamp — calendar Day 5)
- Draft **#3** script repaired; pipeline restarted

---

## Commands

```bash
python3 -m shorts_bot.production.queue_cli --list
python3 -m shorts_bot.production.queue_cli --repair-draft 3
python3 -m shorts_bot.production.queue_cli --run-next --no-upload
python3 -m shorts_bot.production.ops_status_cli
```
