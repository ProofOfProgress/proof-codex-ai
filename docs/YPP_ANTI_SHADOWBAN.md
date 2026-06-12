# YPP / anti-shadowban operating rules

Research-backed rules for **Soft Continuity** when running a mostly automated AI pipeline. YouTube does not shadowban channels for using AI tools — it enforces **inauthentic content** policy at the channel level.

## What YouTube actually targets (Jul 2025+)

Policy rename: **repetitious content** → **inauthentic content**.

Official definition ([YouTube Help](https://support.google.com/youtube/answer/1311392)):

- Mass-produced or repetitive content
- Template with little variation across videos
- Easily replicable at scale
- Slideshows, templated storylines, scrolling text with minimal narrative value
- AI-generated generic templates without the creator's original perspective

**Not banned:** AI-assisted editing, research, TTS of your own scripts, stick-figure animation, automation as a **tool** when output has a recognizable creative voice.

YouTube Creator Liaison (2025): policies apply the same whether you shoot on camera, animate, or use AI — the question is whether the video expresses **human creativity**, not which tool built it.

## What fully automated AI farms get hit for

These patterns correlate with demonetization, suppressed recommendations, and "feels shadowbanned" reports:

| Pattern | Why it's risky |
|---------|----------------|
| Same script structure every upload, keyword swapped | Template repetition — core inauthentic signal |
| Slideshow + stock + generic TTS, no story | No editorial value |
| 5–20 Shorts uploaded same day | Spam / mass-production signal |
| Identical hooks/titles with one word changed | Low variation across channel |
| Lecture-mode third-person scripts | Reads as AI content farm |
| Spam phrases ("in today's fast-paced world", "let's dive in") | Obvious AI slop |
| ALL CAPS clickbait titles | Engagement bait / misleading metadata |
| Mass identical comment auto-replies | Spam & deceptive practices |
| Re-uploading same topic because views were flat | Duplicate spam — fix hook first |

**Flat views after upload** is often weak hook/retention, not a shadowban. Do not duplicate-upload the same topic the same day.

## Soft Continuity countermeasures (built into bot)

### Operating rules (agent memory)

Seeded from `data/operating_rules_seed.md` and `shorts_bot/compliance/inauthentic_rules.py` → injected into strategist + draft prompts.

### Upload guard (automatic)

`shorts_bot/compliance/upload_guard.py` runs before every YouTube upload in `finish_draft_pipeline`.

**Blocks upload when:**

- Spam-farm phrase in script/hook
- No personal voice in script (need immersive `you` or lived-experience `I` — not lecture mode)
- Already hit `MAX_UPLOADS_PER_24H` (default: 1)
- Less than `MIN_HOURS_BETWEEN_UPLOADS` since last upload (default: 20h)
- Same topic within `TOPIC_COOLDOWN_DAYS` (default: 7)
- Same hook within `HOOK_COOLDOWN_DAYS` (default: 14)
- Script Jaccard overlap ≥ `MAX_SCRIPT_OVERLAP_RATIO` (default: 50%) vs recent upload
- **QA iteration titles** `(build vN …)` — mass same-topic uploads
- **`allow_duplicate_draft`** — re-uploading same draft_id (banned under YPP_SAFE_MODE)
- **`upload_series_cli`** — batch upload of all builds (banned unless `YPP_ALLOW_BATCH_SERIES_UPLOAD=true`)
- Hashtags in titles, engagement-bait metadata ("you won't believe", "watch till the end")
- Same scare pillar as previous upload (must rotate reflection / knock / cam / text)
- Duplicate approved draft topic (template repetition)

**Unlisted QA uploads** count toward the 24h cap (`UNLISTED_QA_BYPASS_UPLOAD_COOLDOWN=false` by default).

`auto_daily` calls the same pipeline — render may complete, upload skipped if guard blocks.

### Hard-banned operations (`shorts_bot/compliance/ypp_bans.py`)

| Operation | Why |
|-----------|-----|
| `upload_series_cli` (7 builds / 1 draft) | Mass-produced inauthentic signal |
| `--allow-duplicate-draft` | Same script/topic flood |
| `(build vN …)` in title | QA iteration spam on channel |
| Hashtags in title | Tag-stuffing / misleading metadata |
| `AUTO_UPLOAD_YOUTUBE=true` + `public` without review | No human editorial layer |
| `auto_daily` + auto-approve to public | Factory channel at scale |

Preview iterations **locally only** until one owner-approved upload passes guard.

### Human layer (counts as creative input)

- Crisis/trauma/medical comments → `comments pending`
- Risky improvement proposals need approval
- Niche positioning ("The Minute Before") and stick figures acting beats

### Quality + voice

- Quality gate before upload (`quality_gate_blocks_upload`)
- Resemble **own** voice clone — not impersonation
- Disclose altered/synthetic audio in Studio when prompted

## Configuration (`.env`)

```bash
YPP_SAFE_MODE=true
MAX_UPLOADS_PER_24H=1
MIN_HOURS_BETWEEN_UPLOADS=20
TOPIC_COOLDOWN_DAYS=7
HOOK_COOLDOWN_DAYS=14
MAX_SCRIPT_OVERLAP_RATIO=0.50
UNLISTED_QA_BYPASS_UPLOAD_COOLDOWN=false
YPP_ALLOW_BATCH_SERIES_UPLOAD=false
AUTO_APPROVE_DRAFTS=false
AUTO_UPLOAD_YOUTUBE=false
YOUTUBE_UPLOAD_VISIBILITY=unlisted
AUTO_DAILY_ENABLED=false
```

Set `YPP_SAFE_MODE=false` only when you intentionally override (e.g. non-monetized test channel with owner approval). Never disable on a channel applying for or maintaining YPP.

## If YPP rejects or demonetizes

1. Private/delete templated spam-era videos
2. Upload several weeks of clearly varied, first-person Shorts (guard on)
3. Appeal in Studio with workflow proof — original scripts, not copy-paste templates
4. Switching to live mic is **not required** if the issue was inauthentic repetition

## Related docs

- `docs/VOICEOVER_POLICY.md` — TTS monetization basics
- `docs/COMMENTS.md` — comment automation limits
- `docs/SELF_LEARNING.md` — quality gate + learning loop
