# Top 12 — Long-form + consistent quality (Peripheral)

**Assessed:** 2026-06-12  
**Goal:** Shorts discover · long-form earns watch hours · **same quality bar** both formats.  
**Cost rule:** Reuse Short assets first; cap I2V (`docs/CONTENT_FORMATS.md`).

| # | Priority | What “done” means | Status |
|---|----------|-------------------|--------|
| **1** | **Quality bar for long-form** | Written standards + automated checks before upload | **Done** — `data/LONG_FORM_QUALITY.md`, `long_quality.py` |
| **2** | **Content format profiles** | Short/long modes + I2V budgets in code | **Done** — `content_format.py` |
| **3** | **Long compilation pipeline** | Stitch 3+ Shorts → 16:9 MP4, $0 new I2V | **Done** — `long_compilation_cli.py`, `long_form_render.py` |
| **4** | **16:9 presentation** | Vertical Short readable on TV/desktop (blur pillarbox) | **Done** — `compose_vertical_in_landscape()` |
| **5** | **Chapter timestamps + upload meta** | Description chapters for long uploads | **Done** — `long_upload_meta.py` |
| **6** | **Winner selection** | Pick best Shorts for compilations from packs/DB | **Done** — `winner_selection.py` |
| **7** | **Script expand (Short → long)** | Expand outlier Short to 6–10 min outline | **Done** — `script_expand.py` (template; Gemini hook later) |
| **8** | **Hybrid cost defaults** | Daily Shorts at 3 I2V beats | **Done** — `short_hybrid` profile + render cap |
| **9** | **Long still pack scaffold** | 16:9 still pipeline manifest fields | **Done** — `long_still_pack.py` |
| **10** | **Unified QC gate** | Block upload if long quality fails | **Done** — `long_quality_cli.py` |
| **11** | **Analytics → compile loop** | Retention winners drive next compilation | **Partial** — `winner_selection.py` scores packs + uploads; Studio retention import TBD |
| **12** | **First long upload** | One public compilation on channel | **Blocked** — YouTube upload quota + need **3** polished Shorts live (QC requires 3 segments) |

---

## Consistent quality (Short + long)

Both formats must pass:

1. Hook in line 1 / chapter title matches story  
2. Peripheral brand in description  
3. Synthetic media disclosed  
4. No QA build suffix on public titles  
5. Scare pillar rotated vs last upload  
6. Captions readable (Shorts burned; long ASS when VO pipeline extended)  

Short bar: `data/LONG_FORM_QUALITY.md` + existing `LAUNCH_QUALITY.md` / vision QC.  
Long bar: `long_quality.py` before `upload_canonical_cli` / future `upload_long_cli`.

---

## Next after #12 unblocks

- Bridge VO between stories (hits 8–15 min watch-hour target)  
- Resemble bridge VO merge into compilation  
- Gemini `script_expand` for prose quality (template scaffold ships now)  
- Studio retention import for #11  

---

## Commands

```bash
# Pick drafts with rendered Shorts
python3 -m shorts_bot.production.winner_selection_cli --limit 3

# Build compilation (16:9, blur pillarbox)
python3 -m shorts_bot.production.long_compilation_cli --draft-ids 2,3,1

# QC compilation pack
python3 -m shorts_bot.production.long_quality_cli --pack-dir data/production/long_compilation_001

# Expand winning Short script to long outline
python3 -m shorts_bot.production.script_expand_cli --draft-id 3

# Scaffold long_still pack from outline
python3 -m shorts_bot.production.long_still_pack_cli --draft-id 3

# Upload long (QC gated; needs 3 segments + final_long.mp4)
python3 -m shorts_bot.production.upload_long_cli --pack-dir data/production/long_compilation_001
```
