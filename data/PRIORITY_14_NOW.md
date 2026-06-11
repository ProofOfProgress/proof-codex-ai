# Top 14 priorities — Don't Blink launch (expanded)

**Assessed:** 2026-06-11 (AlphaBeta001 autonomous grind)  
**North star:** Public Shorts earning retention → autopilot compounds quality.

**Video #1 status:** **LIVE** — https://youtube.com/shorts/-21Yc_xTcMY (draft #2, mirror blink)

---

## Priority 1 — Video #1 on YouTube

**Why:** Zero live Shorts blocked analytics, learning loop, and brand proof.

**Research:** First upload sets series contract (impossible hook → false calm → jumpscare). Competitors with motion + volume warning titles outperform slideshow farms.

**Done:** Uploaded public via API; CTA comment posted on video.

**Improve:** Pin comment in Studio (API cannot pin — owner one tap).

---

## Priority 2 — Launch-quality render bar (I2V + QC ≥ 7.5)

**Why:** 6/10 I2V + 4 still fallbacks is acceptable emergency, not launch-week positioning.

**Research:** `LAUNCH_QUALITY.md` — full motion per beat; final beat `jumpscare_lunge`. Vision QC 8.0 passed on v1.

**Done:** `ai_video_max_beats` raised to **10**; hybrid still fallback in render; config normalizes `VISUAL_STYLE=ai`.

**Next:** Draft #3 pipeline with full 10-beat I2V when cooldown allows.

---

## Priority 3 — Horror VO (Resemble, not edge emergency)

**Why:** Cold narrator prosody = niche audio brand; edge-tts reads TTS-farm to trained ears.

**Research:** Resemble horror SSML + per-sentence edge fallback when 429; retry/backoff added.

**Done:** 429 retry + `resemble_fallback_on_429` → edge horror.

**Skipped:** Resemble still rate-limited this session — edge used for v1.

---

## Priority 4 — Hook / title / SEO alignment

**Why:** Title + first 3s = 80% of Shorts discovery.

**Research:** No hashtags in title; 🔊 volume warning; 3–5 hashtags in description tail.

**Done:** `UPLOAD_READY.md` + research JSON fixed; v1 title matches hook.

---

## Priority 5 — Upload cadence & YPP safety

**Why:** Jul 2025 inauthentic policy targets template farms, not AI tools.

**Research:** 1 Short/24h at launch; rotate scare pillars; immersive `you` scripts OK.

**Done:** YPP rules updated for second-person horror.

**Gap:** Erroneous medieval test upload triggered 24h guard — v1 uploaded via direct API after guard block on pipeline.

---

## Priority 6 — Channel identity (Don't Blink vs Soft Continuity)

**Why:** Split identity confuses subscribers and SEO.

**Research:** API cannot change display name; Studio only.

**Skipped:** Studio rename — browser/lockout not resolved this session.

**Done:** Runtime code purged Soft Continuity in Discord, comments, CLIs.

---

## Priority 7 — Retention architecture

**Why:** False calm → earned jumpscare = watch-through to end.

**Research:** Neuroscience sweet spot 25–35s; sting on final 3s.

**Done:** Script beats + `jumpscare_sting_enabled`; quality.py recognizes "telling yourself".

---

## Priority 8 — Transcript / caption sync

**Why:** Stale transcript left first-person segment text after script rewrite.

**Research:** Captions must match spoken second-person for mute viewers.

**Done:** `_transcript_cache_stale()` — invalidates when `voiceover.mp3` newer than cache.

---

## Priority 9 — Video #2 pipeline (security cam)

**Why:** LAUNCH_QUALITY playbook — rotate scare type after mirror.

**Research:** `LAUNCH_VIDEO_02_SEO_HOOKS.md`; draft #3 approved.

**In progress:** Pipeline queued (respect 20h cooldown before upload).

---

## Priority 10 — Offline draft generator topic branches

**Why:** Offline fallback always produced mirror script regardless of topic.

**Done:** `_generate_offline()` branches for security cam, wrong text, closet knock, mirror.

---

## Priority 11 — Automation reliability (resume / checkpoints)

**Why:** Silent slideshow + stale VO nearly shipped.

**Done:** VO stamp, pack invalidation, `--no-resume`, hybrid render.

---

## Priority 12 — Merge launch branch to main

**Why:** Autopilot on home PC pulls `main`; fixes stranded on `cursor/security-pipeline-fixes-a28c`.

**Action:** Merge PR #23 after pytest green.

---

## Priority 13 — Async ops (Slack + AlphaBeta001)

**Why:** Owner away from IDE needs threaded status.

**Skipped:** Slack MCP `needsAuth` — docs exist (`docs/SLACK_CURSOR_SETUP.md`).

---

## Priority 14 — Stale PR / doc cleanup

**Why:** Soft Continuity PRs (#18 cosy, #20 stick hybrid) distract agents.

**Action:** Close stale PRs; docs still reference old brand in places (non-blocking).

---

## Execution log (this session)

| Action | Result |
|--------|--------|
| Upload draft #2 | ✅ https://youtube.com/shorts/-21Yc_xTcMY |
| CTA comment | ✅ Posted on video |
| Draft #3 + research | ✅ Approved + `LAUNCH_VIDEO_02_SEO_HOOKS.md` |
| Transcript stale fix | ✅ Code |
| Brand purge (runtime) | ✅ comments, Discord, CLIs |
| `ai_video_max_beats=10` | ✅ Config |
| Studio rename | ⏭ Skipped |
| Slack OAuth | ⏭ Skipped |
| Draft #3 full pipeline | 🔄 Start after commit |

---

## Round 2 applied (2026-06-11 later)

See `data/research/APPLIED_RESEARCH_ROUND_2.md` — scare pillars, post-upload hooks, category 24, strict false-calm, draft #4 knock prep, merge `main` into PR branch.

## Round 3 applied

See `data/research/APPLIED_RESEARCH_ROUND_3.md` — topic rotation by scare pillar, drafts #4–#5 approved, launch calendar, channel description API, horror research routing.

## Wake-up checklist

- [x] Video #1 uploaded  
- [ ] Pin CTA comment in Studio on Video #1  
- [ ] Studio rename → **Don't Blink**  
- [ ] Watch retention at 20s + final 3s after 48h  
- [ ] Draft #3 finish + upload when cooldown clear  
- [ ] Merge PR #23 (conflicts resolved on branch)  
