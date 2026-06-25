# Production research — methods, risks, and system upgrades

Deep research (June 2026) on faceless Shorts production, YPP safety, AV sync, and what we implemented in **Shorts Bot**.

## Executive summary

| Finding | Action taken |
|---------|----------------|
| **Mass-identical templates** trigger inauthentic-content flags | Per-draft **variety engine** (zoom, caption offset, figure position, cut length) |
| **Single-axis variety** (voice only) is insufficient | Rotate 5+ axes every draft (`variety.py`) |
| **TurboScribe browser** is fragile | `segment_sync.py` — cache + script-duration fallback + segment merge |
| **Quality gate only at upload** wastes TTS/render credits | **Pre-flight gate** before humanize/TTS (`pipeline.py`) |
| **visual_beats ignored** after draft generation | Saved to `data/draft_meta/` → wired into `scene_plan` + stick render |
| **No pipeline resume** on failure | `pipeline_state.json` checkpoints per draft |
| **Silent daily failures** | `automation/alerts.py` → `data/ALERTS.md` |
| **Stale research cache** | `RESEARCH_CACHE_DAYS` TTL + daily force refresh option |
| **Static slideshow retention** | Optional Ken Burns per segment (`VIDEO_KEN_BURNS=true`) |
| **Word-level sync** best via forced alignment | TurboScribe Whale (primary); future: local WhisperX / stable-ts |

---

## 1. Industry production methods (2025–2026)

### A. Modular “inspectable” pipeline (recommended)

Human editorial judgment at each stage — not black-box one-click tools:

1. **Research** — Trends, competitors, viewer moment (our `deep_research_topic`)
2. **Script** — LLM draft + humanize pass + AI-detect loop
3. **Voice** — Cloned VO (Resemble) with consistent channel voice
4. **Sync** — Word/sentence timestamps → visual cuts
5. **Visuals** — Stick figures acting each beat (ChainsFR) or calm stills
6. **Assembly** — ffmpeg 1080×1920 + ASS captions
7. **QC** — Pre-flight script + post-render video checks
8. **Upload** — API or Studio; YPP guard; 1 Short / 24h

### B. What platforms penalize

Sources: [Precheck originality guide](https://precheck.tools/platforms/youtube/youtube-originality-guide/), [ReelForge 2026 detection](https://reelforgeai.io/blog/how-platforms-detect-ai-video-content-2026), [OutlierKit AI slop crackdown](https://outlierkit.com/resources/youtube-ai-slop-crackdown-2026/).

- End-to-end upload with **no human creative decisions**
- **Identical structure** across dozens of videos (same hook shape, same cut rhythm, same caption style)
- **Bulk upload** spikes (we enforce max 1/24h)
- **Reused content** without transformative commentary
- Missing **AI disclosure** when synthetic voice is realistic

### C. What still works for faceless Shorts

- **First-person help** — “I used to… here’s what I do now” (Soft Continuity voice)
- **Mute-safe visual story** — stick figure acts each line without VO
- **Per-video differentiation** — topic, hook, beats, motion, caption band
- **Human-in-the-loop** — approve improvements, serious comments; quality gates
- **Disclose** synthetic audio in Studio when prompted

---

## 2. AV sync methods (ranked)

| Method | Accuracy | Cost | Our status |
|--------|----------|------|------------|
| **TurboScribe Whale** | Best (browser) | Paid Unlimited | Default when logged in |
| **SRT / transcript cache** | Good | Free | `turboscribe_transcript.txt` + `segment_sync` |
| **Script scaled to MP3** | Good | Free | `segments_from_script_for_duration()` |
| **Raw script WPS** | Weak | Free | Legacy fallback only |
| **WhisperX + forced align** | Excellent | GPU/local | **Planned** — see below |
| **stable-ts align** | Excellent for clean TTS | API/local | **Planned** for Resemble VO |

### WhisperX / stable-ts (next step)

For Resemble AI voice (clean audio), **forced alignment** against the approved script beats TurboScribe UI fragility:

```bash
# Future optional path (not in requirements yet):
pip install whisperx  # or stable-ts
# Align voiceover.mp3 to finalized script → word-level SRT → segment_sync
```

Config hook (future): `SYNC_PROVIDER=turboscribe|whisperx|script`

---

## 3. Video quality stack

See also `docs/SHORTS_ALIGNMENT.md`.

| Setting | Default | Why |
|---------|---------|-----|
| `VIDEO_CRF` | 18 | YouTube re-encodes; start high quality |
| `VIDEO_PRESET` | slow | Better compression efficiency |
| `VIDEO_AUDIO_BITRATE_K` | 192 | YouTube AAC ceiling |
| Scale | lanczos 1080×1920 | Sharp vertical output |
| `VIDEO_KEN_BURNS` | false | Subtle zoom in/out per cut — slower render |
| `CAPTION_MODE` | ffmpeg | Single ASS source; no double captions |

Post-render **video QC** (`video_qc.py`):

- Min/max duration (20–58s Shorts band)
- File size sanity
- Mean volume (quiet / clip warnings)

---

## 4. Variety engine (anti-fingerprint)

`shorts_bot/production/variety.py` — deterministic per `draft_id`:

| Axis | Rotates |
|------|---------|
| Ken Burns | in / out / none |
| Caption Y | ±24px from anchor |
| Figure X | ±36px from center |
| Cut length bias | 0.88×–1.12× merge factor |
| Hook pacing label | calm / normal / brisk (metadata) |

Disable: `PRODUCTION_VARIETY_ENABLED=false`

**Research insight:** classifiers cluster on metadata, motion, caption cadence, and audio fingerprint — not just voice. Rotating multiple axes per upload is the practical defense at scale.

---

## 5. Visual beats → stick figures

Draft generator returns `visual_beats` (3–5 mute-safe shots). Stored in `data/draft_meta/draft_{id}.json`.

Pipeline uses beats as **pose hints** in `scene_plan.py`:

- Bathroom / stall → `Pose.HUDDLED`
- Walk / excuse → `Pose.WALKING`
- Breath / reset → `Pose.BREATHING`

New poses render in `render_stickfigures.py`.

---

## 6. Pipeline checkpoints

`data/production/draft_{id}/pipeline_state.json`:

```
preflight → humanize → voiceover → turboscribe → pack → render → video_qc → metadata → upload
```

Resume on retry skips completed steps when output files exist.

Report: `pipeline_report.json` (timings + messages).

---

## 7. Automation alerts

Failures in daily autopilot write to:

- `data/ALERTS.md` (last ~40 events)
- `channel_state.last_automation_alert` in SQLite

Check: read `data/ALERTS.md` after being away, or `status` in web chat.

---

## 8. Research cache

- `RESEARCH_CACHE_DAYS=7` — stale topics re-research automatically
- `DAILY_RESEARCH_FORCE_REFRESH=true` — daily run always hits web/trends (default on)

---

## 9. Config reference (new / important)

```env
# Quality gates
QUALITY_GATE_BLOCKS_RENDER=true
QUALITY_GATE_BLOCKS_UPLOAD=true
VIDEO_QC_BLOCKS_UPLOAD=true

# Variety
PRODUCTION_VARIETY_ENABLED=true

# Motion
VIDEO_KEN_BURNS=false

# Research
RESEARCH_CACHE_DAYS=7
DAILY_RESEARCH_FORCE_REFRESH=true

# Daily schedule (UTC)
AUTO_DAILY_ENABLED=true
AUTO_DAILY_HOUR=11
AUTO_DAILY_MINUTE=0
```

---

## 10. Recommended operating rhythm (while away)

1. **Daily autopilot** runs at `AUTO_DAILY_HOUR:AUTO_DAILY_MINUTE` UTC if web server is up
2. Each run: fresh research → draft → auto-approve → finish pipeline → optional upload
3. **YPP guard** blocks >1 upload/24h and topic/hook cooldowns
4. Check `data/ALERTS.md` if something breaks
5. **OAuth upload:** `YOUTUBE_OAUTH_UPLOAD=1 python3 -m shorts_bot.youtube.auth_cli` for API uploads
6. **Studio fallback:** `studio_upload.py` when token lacks upload scope

---

## 11. Future improvements (not yet built)

| Item | Impact |
|------|--------|
| Local WhisperX / stable-ts sync | Remove TurboScribe browser dependency |
| LLM scene_plan (not keyword-only) | Richer poses per niche |
| Background music ducking | Retention + polish |
| CapCut Playwright operator | Human override path |
| TikTok export + safe zones | When user says go |
| Cost accounting per draft | Resemble + TS + render time |
| Mute-preview validation | Jenny 05 “review on mute” gate |

---

## 12. Sources

- [YouTube originality / reused content — Precheck](https://precheck.tools/platforms/youtube/youtube-originality-guide/)
- [Platform AI detection & variety — ReelForge 2026](https://reelforgeai.io/blog/how-platforms-detect-ai-video-content-2026)
- [AI slop crackdown — OutlierKit](https://outlierkit.com/resources/youtube-ai-slop-crackdown-2026/)
- [TubeBuddy monetization best practices](https://www.tubebuddy.com/blog/youtube-ai-monetization-best-practices/)
- [FFmpeg YouTube encoding 2026](https://ffmpeg-cookbook.com/en/articles/youtube-ffmpeg-settings/)
- [WhisperX word-level timestamps](https://github.com/m-bain/whisperX)
- Internal: `docs/SHORTS_ALIGNMENT.md`, `docs/YPP_ANTI_SHADOWBAN.md`, `docs/CHAINSFR_RESEARCH.md`
