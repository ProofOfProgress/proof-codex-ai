# Top 7 priorities right now — Don't Blink launch

**Assessed:** 2026-06-11 (AlphaBeta001 overnight grind)  
**North star:** First public Short that earns retention + sets series contract — then compound via automation.

**Current blockers:** Draft #2 rendered as **slideshow** (shell `VISUAL_STYLE=ai` overrode `.env`), edge-tts VO (Resemble 429), vision QC failed on near-black hook, channel display name still **Soft Continuity** (24h Studio lockout).

---

## Priority 1 — Ship launch-quality Video #1 (I2V + horror VO + QC pass)

### Why this is #1

- **Zero videos live** — every other lever (analytics learning, cadence, brand recognition) is blocked until something ships.
- Draft #2 `final_short.mp4` exists but manifest shows `render_mode: slideshow`, `clips_rendered: 0` — competitors in mirror-horror niche use **motion**; static Ken-Burns reads as AI farm.
- Vision QC scored **0.0** (near-black hook frame) — upload guard would block anyway.
- First Short sets the **series contract**: impossible hook → false calm → earned jumpscare in last 3s.

### Deep research — what “good” looks like

| Signal | Source / reason |
|--------|-----------------|
| Hook in first 3s spoken | YouTube Shorts weights opening audio; mirror/blink is mute-safe *and* spoken |
| 6–8 beats, 2–3s cuts | Jenny 06 retention; horror research (`HORROR_PSYCHOLOGY_DEEP_RESEARCH.md`) |
| False calm before scare | Dread buildup — swipe bait at beat 5–6, sting at end |
| I2V per beat | `LAUNCH_QUALITY.md` — Don't Blink = full motion, not FLUX slideshow |
| Vision QC ≥ 7.5 | Catches black frames, frozen clips, off-sync horror |
| Resemble horror SSML | Cold narrator prosody; edge fallback is acceptable emergency only |

### How to make it better (actions)

1. **Force `VISUAL_STYLE=ai_video`** — normalize legacy `ai` → `ai_video` in config; invalidate pack checkpoint when manifest is slideshow.
2. **Rewrite script second-person** — hook: *You blinked at the mirror — your reflection blinked one second later.*
3. **Regenerate VO** — Resemble with retry/backoff on 429; invalidate stale edge checkpoint.
4. **Re-run pipeline** — pack → I2V (6 beats capped) → render → vision QC.
5. **Do not upload** until QC ≥ 7.5 and `render_mode: video_clips`.

---

## Priority 2 — Hook / title / description / hashtag SEO alignment

### Why this is #2

- **Discovery is title + first 3 seconds** — 200 views in 7 days on old branding proves *some* surface area exists; launch metadata must not waste it.
- Current `UPLOAD_READY.md` title has **hashtags in title** (`#horror #shorts`) — wastes chars; YouTube shows first 3 desc hashtags above title anyway (`LAUNCH_VIDEO_01_SEO_HOOKS.md`).
- Research JSON `title_formula` drifted from SEO doc (competitor clickbait pattern).

### Deep research

| Element | Best practice | Our gap |
|---------|---------------|---------|
| Title | ≤70 chars, 🔊 volume warning, keyword in first 40 chars, **no hashtags** | Hashtags in title from research blob |
| Description | Line 1–2 = primary keyword; 3–5 hashtags at end; CTA comment | Hook still first-person in desc |
| Backend tags | 5–8 Studio tags, mirror/reflection specific | OK |
| Spoken hook | Must match title promise | Script/title mismatch (I vs you) |

**Winner title (from research):**
```
🔊 You blinked — your reflection blinked one second later
```

### How to make it better

1. Strip hashtags from `_title_from_research()`; prefer `LAUNCH_VIDEO_01_SEO_HOOKS.md` formula.
2. Fix `the-mirror-reflection-....json` `title_formula`.
3. Regenerate `UPLOAD_READY.md` after script rewrite.
4. A/B alts documented in research — only after video 1 baseline metrics.

---

## Priority 3 — Upload cadence & YPP / inauthentic safety

### Why this is #3

- **1 Short / 24h** is correct for launch (`max_uploads_per_24h=1`, `min_hours_between_uploads=20`).
- 2×/day is a **spam-farm signal** until retention proves channel isn't template output (Jul 2025 inauthentic policy).
- Tension: old YPP rules required first-person `I/my`; horror quality wants second-person `you` — lecture-style third-person is the real risk.

### Deep research

YouTube targets **mass-produced template Shorts** (identical skeleton, keyword swap, slideshow+TTS). Safe counter-signals:

- Editorial variety (topic/hook cooldown 7–14d)
- Impossible-detail micro-stories (not listicles)
- Motion + sync (not carousel)
- Human queue for serious comments
- Synthetic media disclosure

### How to make it better

1. Keep **1/day** until 5+ uploads with retention data.
2. Update `inauthentic_rules.py` — accept immersive second-person horror (`you` + sufficient length), block generic lecture.
3. Never upload draft #2 slideshow — would train wrong quality bar.
4. Owner: disclose altered/synthetic audio in Studio when prompted.

---

## Priority 4 — Channel identity (name, eye brand, series contract)

### Why this is #4

- Display name still **Soft Continuity** — API cannot change (`channelTitleUpdateForbidden`); Studio returns 24h lockout.
- Handle `@alphabeta0-c1m`, horror banner/PFP, description already **Don't Blink** — split identity confuses subscribers.
- Series contract = every Short ends with earned scare; title 🔊 trains expectation.

### How to make it better

1. **Owner (after lockout):** Studio → Customization → name **Don't Blink** (alts: Never Blink, Dont Look Away).
2. Pipeline: all upload meta says **Don't Blink** not Soft Continuity.
3. Pin comment template: "What should the next impossible detail be?"
4. Consistent pillar rotation (mirror = Wrong reflection) — document in `channel/brand/identity.md`.

---

## Priority 5 — Retention architecture (false calm, beats, length, sting)

### Why this is #5

- Horror Shorts fail when scare is **unearned** (competitor gap in research: "trick/challenge" framing without dread).
- Draft #2 QC warned: **no false-calm beat** — reduces watch-through to jumpscare.
- `jumpscare_sting_enabled` on render — good; must sync with visual lunge beat.

### Deep research (from `jumpscare-timing-misdirection-neuroscience-...json`)

- **Prediction error** drives blink-delay hook (mirror pillar).
- **False calm** lowers guard — quiet VO + slow motion before lunge.
- **25–35s** total — not 60s slow burn.
- Final 3s = full-frame scare + audio sting (🔊 in title).

### How to make it better

1. Script beat 5: *You turned away, telling yourself it was just tired eyes.*
2. Enforce in `quality.py` (already warns) — promote false-calm missing to **issue** at launch.
3. Vision QC: dark hook → warning not auto-fail if avg score OK (already partially fixed).
4. Analytics after publish: retention at **20s** and **final 3s** → reflect loop.

---

## Priority 6 — Automation reliability (env, TTS, I2V, resume, vision QC)

### Why this is #6

- Owner wants **sleep mode** — pipeline must not silently degrade (slideshow, stale VO, skipped QC).
- Root causes from draft #2 log:
  - `VISUAL_STYLE=ai` in shell
  - Resemble **429** → edge without invalidating checkpoint
  - Resume skipped re-VO when `voiceover.mp3` existed
  - Vision QC skipped when Gemini path failed

### How to make it better

1. **Config:** `ai` → `ai_video` normalization.
2. **Resemble:** exponential backoff on 429/5xx.
3. **VO stamp:** `voiceover_stamp.json` — invalidate resume if provider/delivery changed.
4. **Pack invalidation:** re-pack if `render_mode != video_clips` when `ai_video` required.
5. **`finish_cli --no-resume`** for forced full rebuild.
6. **`auto_daily`** must surface pipeline failures to Discord/Slack when wired.

---

## Priority 7 — Owner ↔ agent async (Slack, AlphaBeta001 identity)

### Why this is #7

- Owner sleeping — needs **threaded updates** without IDE (`docs/SLACK_CURSOR_SETUP.md`).
- Slack MCP = `needsAuth` until owner OAuth in Cursor Desktop.
- Manager is **AlphaBeta001**, not the channel — reduces confusion in ops threads.

### How to make it better

1. Owner: authenticate Slack MCP + create `#dont-blink-ops`.
2. Post overnight summary: draft status, QC score, blockers, Studio rename reminder.
3. Use `@cursor` for course corrections ("priorities changed", "upload now").
4. `data/SLACK_SETUP_CHECKLIST.md` — tick items as done.

---

## Execution order tonight

| Step | Owner | Agent |
|------|-------|-------|
| Fix pipeline code | — | ✅ this session |
| Rewrite draft #2 script | — | ✅ this session |
| Re-run I2V pipeline | — | ✅ this session |
| Studio rename | ⏳ after 24h | remind in summary |
| Slack OAuth | ⏳ Desktop | docs ready |
| Upload video #1 | approve when QC passes | queue metadata |

---

## Success criteria (wake-up checklist)

- [ ] `data/production/draft_2/manifest.json` → `render_mode: video_clips`, `clips_rendered` ≥ 1
- [ ] `pipeline_report.json` → vision QC score ≥ 7.5, `success: true`
- [ ] `UPLOAD_READY.md` title matches SEO doc (no hashtags in title)
- [ ] Script uses **you** + false calm + lunge ending
- [ ] `python -m pytest tests/ -q` green
- [ ] PR updated with this doc + pipeline fixes

**Do not upload** until owner reviews `final_short.mp4` unless they pre-authorized autopublish and QC fully passes.
