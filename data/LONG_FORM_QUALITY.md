# Long-form quality bar — Peripheral

Same brand promise as Shorts: **faceless horror, earned dread, Peripheral label.**

---

## Compilation (`long_compilation`)

| Check | Bar |
|-------|-----|
| Stories | **3–5** finished Shorts, each passed Short QC |
| Per-Short retention | Prefer uploads with best end retention (manual/Studio until #11) |
| Total duration | **8–15 minutes** |
| Audio | No clipped stings; volume consistent between stories |
| Visual | 16:9 blur pillarbox — full 9:16 frame visible, no crop of captions |
| Bridges | Optional 1–2 sentence VO between stories (same narrator) |
| Chapters | Timestamp per story in description |
| Title | e.g. “3 scary stories for people home alone at night \| Peripheral” |
| No new I2V | Reuse existing MP4 only |

---

## Still narrative (`long_still`)

| Check | Bar |
|-------|-----|
| Words | **800–1400** (~6–10 min VO) |
| Beats | **12–20** visual segments (~25–40s each) |
| Structure | Hook → 3 escalations → false calm → finale scare |
| Stills | 16:9 FLUX, horror palette, no cosy |
| Motion | Ken Burns only — **no I2V** unless `long_hybrid` |
| Script | Expanded from **winning** Short pillar — not generic |

---

## Hybrid long (`long_hybrid`)

| Check | Bar |
|-------|-----|
| I2V cap | **≤4** new clips (`content_format.py`) |
| Reuse | ≥50% runtime from existing Short `clips/` |
| Hero beats | Hook + finale mandatory motion |

---

## Shared with Shorts

- Second-person **you**, impossible detail hook  
- 🔊 volume warning when finale sting  
- `containsSyntheticMedia` on upload  
- Rotate scare pillar vs previous public video  
- Peripheral + don't blink in description  

---

## Automated

`python3 -m shorts_bot.production.long_quality_cli --pack-dir PATH`

Fails closed on: too few segments, duration out of range, missing source videos.
